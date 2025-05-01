#############################################
#############################################
##     select and run checks  endpoint     ##
#############################################
#############################################

import os, re, time, datetime, logging
from flask import request, session, render_template, current_app, send_file

import setchks_app
from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.ts_and_cs.wrapper import accept_ts_and_cs_required
from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.redis.rq_utils import start_specific_rq_worker
from setchks_app.setchks.available_setchks import available_setchks
from setchks_app.jobs_manager.jobs_manager import SetchksJobsManager
from setchks_app.setchks.run_queued_setchks import run_queued_setchks



logger=logging.getLogger(__name__)

@auth_required
def select_and_run_checks():
    print("ENTER METADATA FROM KEYS", request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    bc=Breadcrumbs()
    bc.set_current_page("select_and_run_checks")

    setchks_session.selected_setchks=[]
    for sc in available_setchks:
        this_setchk = setchks_app.setchks.setchk_definitions.setchks[sc]
        if (
            "ALL" in this_setchk.setchk_data_entry_extract_types or 
            setchks_session.data_entry_extract_type in this_setchk.setchk_data_entry_extract_types
            ) and (
            setchks_session.sct_version_mode in this_setchk.setchk_sct_version_modes    
            ):
            setchks_session.selected_setchks.append(this_setchk)
    # logger.debug(setchks_session.selected_setchks)

    # get update on queued jobs if in state 2,3,4
    setchks_jobs_manager=setchks_session.setchks_jobs_manager
    if setchks_jobs_manager is not None:
        time0=time.time()
        job_status_report=setchks_jobs_manager.update_job_statuses()
        logger.debug("\n".join(job_status_report))
        logger.debug(f"Time taken to get job statuses = {time.time()-time0}")

    processing_status_changed_this_visit=False
    if (setchks_session.processing_status=="2_PREPROCESSING") and (setchks_session.preprocessing_done):
        setchks_session.processing_status="3_CHECKS_RUNNING"
        processing_status_changed_this_visit=True
    elif (setchks_session.processing_status=="3_CHECKS_RUNNING") and (setchks_session.all_CHKXX_finished):
        setchks_session.processing_status="4_CREATING_REPORT"
        processing_status_changed_this_visit=True
    elif (setchks_session.processing_status=="4_CREATING_REPORT") and (setchks_session.excel_file_available):
        setchks_session.processing_status="5_REPORT_AVAILABLE"
        processing_status_changed_this_visit=True

    # if in state 2,3,4 see if state changes based on update on queued jobs 
    # if state does change set flag "state_changed_this_visit"
    # tests will be of form
    # if setchks_session.processing_status=="3_CHECKS_RUNNING" and state_changed_this_visit:
    #   ... launch checks

    if (
        "do_preprocessing" in request.args and setchks_session.processing_status=="1_CHECKS_READY_TO_RUN"
        and (
             setchks_jobs_manager is None
             or setchks_jobs_manager.jobs_running==False 
             )
        ):

        setchks_session.time_started_processing=datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S')
        setchks_session.processing_status="2_PREPROCESSING"
        # if "environment" in setchks_session.__slots__: # temporary protection for people with old setchks_session objects (13/2/24)
        setchks_session.app_version=current_app.config["VERSION"]
        setchks_session.environment=current_app.config["ENVIRONMENT"]
            

        # start_rq_worker_if_none_running()
        start_specific_rq_worker(worker_name="worker_long_jobs")
        start_specific_rq_worker(worker_name="worker_short_jobs")
        # setchks_session.setchks_results={}  
        # setchks_session.setchks_run_status={}

        if not setchks_session.preprocessing_failed:
            run_in_rq=True
            if run_in_rq:
                setchks_jobs_manager=SetchksJobsManager(setchks_session=setchks_session)
                setchks_session.setchks_jobs_manager=setchks_jobs_manager
                setchks_jobs_manager.launch_job(
                    do_preprocessing=True,
                    setchks_session=setchks_session,
                    )
                job_status_report=setchks_jobs_manager.update_job_statuses()
                logger.debug("\n".join(job_status_report))
            else:
                logger.debug("Doing preprocessing ..: ")
                setchks_session.do_SCT_release_dependent_preprocessing()
        else:   # quick and dirty way to stop the auto reload generating endless loop
                # if preprocessing fails.
            setchks_session.preprocessing_done=True # even though it isn't..
                
    
    # if "run_checks" in request.args:
    if setchks_session.processing_status=="3_CHECKS_RUNNING" and processing_status_changed_this_visit:    
            setchks_session.setchks_jobs_list=run_queued_setchks(
            setchks_list=setchks_session.selected_setchks, 
            setchks_session=setchks_session,
            )

    # if "generate_report" in request.args:
    if setchks_session.processing_status=="4_CREATING_REPORT" and processing_status_changed_this_visit:
        logger.debug("Report requested")
        if not setchks_session.excel_file_generation_failed:
            user_tmp_folder="/tmp/"+setchks_session.uuid
            os.system("mkdir -p " + user_tmp_folder)
            name_prefix=re.sub(r' ',"_",setchks_session.vs_name)
            name_prefix=re.sub(r'[^a-zA-Z0-9_-]',"",name_prefix)
            if len(name_prefix)>30:
                name_prefix=name_prefix[0:30]
            excel_filename="%s/%s_vsmt_setchecks_output_%s.xlsx" % (user_tmp_folder,  name_prefix, datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S'))
            setchks_session.excel_filename=excel_filename
            
            # propose store MI of summary and setchks_session here so that stored
            # if excel generation fails
            setchks_app.mgmt_info.handle_summary_info.store_summary_dict_to_db(setchks_session=setchks_session)
            setchks_app.mgmt_info.handle_setchks_session.store_setchks_session(setchks_session=setchks_session)
            run_in_rq=True
            if run_in_rq:
                setchks_jobs_manager.launch_job(
                    generate_excel=True,
                    setchks_session=setchks_session,
                    )
                job_status_report=setchks_jobs_manager.update_job_statuses()
                logger.debug("\n".join(job_status_report))
            else:
                logger.debug("Generating excel ..: " + excel_filename)
                setchks_session.generate_excel_output()
        else: # quick and dirty way to stop the generate report autoclick generating endless loop
              # if excel file generation fails.
            setchks_session.excel_file_available=True # even though it isn't..
            
    # store excel file to MI here
    if setchks_session.processing_status=="5_REPORT_AVAILABLE" and processing_status_changed_this_visit:    
        setchks_app.mgmt_info.handle_excel_file.store_excel_file(setchks_session=setchks_session)
                
    if "download_report" in request.args and setchks_session.processing_status=="5_REPORT_AVAILABLE":
        if setchks_session.excel_file_generation_failed:
            pass
        else:
            return send_file(setchks_session.excel_filename)

    return render_template('select_and_run_checks.html',
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                           setchks_session=setchks_session,
                           all_setchks=setchks_app.setchks.setchk_definitions.setchks,
                            )