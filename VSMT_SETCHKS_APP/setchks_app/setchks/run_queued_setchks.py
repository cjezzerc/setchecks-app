import os, datetime

from rq import Queue
from rq.job import Job
# from redis import Redis
from setchks_app.jobs_manager.jobs_manager import SetchksJobsManager


import logging
logger=logging.getLogger(__name__)

from setchks_app.redis.get_redis_client import get_redis_string, get_redis_client

def run_queued_setchks(setchks_list=None, setchks_session=None, run_in_rq=True):
    setchks_jobs_manager=SetchksJobsManager(setchks_session=setchks_session)
    setchks_session.setchks_jobs_manager=setchks_jobs_manager
    to_run_if_gatekeeper_not_passed=["CHK02_IDS_IN_RELEASE", "CHK20_INCORR_FMT_SCTID",]
    if setchks_session.data_entry_extract_type=="EXTRACT":
        to_run_if_gatekeeper_not_passed.append("CHK01_APPROP_SCTID")
    # queue up (or directly run) the setchks
    for setchk in setchks_list:
        if run_in_rq:
            if setchks_session.passes_gatekeeper or setchk.setchk_code in to_run_if_gatekeeper_not_passed:
                setchks_jobs_manager.launch_job(
                    setchk=setchk,
                    setchks_session=setchks_session,
                    )
        #         job_status_report=setchks_jobs_manager.update_job_statuses()
        #         logger.debug("\n".join(job_status_report))
        # else:
            logger.debug("Running ..: " + str(setchk.setchk_code))
            setchk.run_check(setchks_session=setchks_session)
    job_status_report=setchks_jobs_manager.update_job_statuses()
    logger.debug("\n".join(job_status_report))

    # # queue up (or directly run) excel generation 
    # user_tmp_folder="/tmp/"+setchks_session.uuid
    # os.system("mkdir -p " + user_tmp_folder)
    # excel_filename="%s/setchks_output_%s.xlsx" % (user_tmp_folder,  datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S'))
    # setchks_session.excel_filename=excel_filename

    # if run_in_rq:
    #     setchks_jobs_manager.launch_job(
    #         generate_excel=True,
    #         setchks_session=setchks_session,
    #         )
    #     job_status_report=setchks_jobs_manager.update_job_statuses()
    #     logger.debug("\n".join(job_status_report))
    # else:
    #     logger.debug("Generating excel ..: " + excel_filename)
    #     setchks_session.generate_excel_output()
    return
