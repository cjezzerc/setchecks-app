import os
import os.path
import sys
import datetime

import logging
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
logger=logging.getLogger(__name__)

location=os.path.abspath(os.getcwd())
print(location)
sys.path.append(location+"/../VSMT_UPROT_APP/")

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils

import vsmt_uprot.terminology_server_module
import vsmt_uprot.vsmt_valueset
import setchks_app.setchks.setchks_session
import setchks_app.setchks.setchk_definitions 
import setchks_app.setchks.run_queued_setchks

from setchks_app.data_as_matrix.columns_info import ColumnsInfo
from setchks_app.data_as_matrix.marshalled_row_data import MarshalledRow


from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.gui import gui_setchks_session
from setchks_app.sct_versions import get_sct_versions
from setchks_app.sct_versions import graphical_timeline

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app, send_file,
)
from werkzeug.exceptions import abort

bp = Blueprint('setchks_app', __name__)

# This list should probably come from a config file in due course
# available_setchks=['CHK20_INCORR_FMT_SCTID', 'CHK04_INACTIVE_CODES', 'CHK06_DEF_EXCL_FILTER']
available_setchks=['CHK04_INACTIVE_CODES', 'CHK06_DEF_EXCL_FILTER']

from pymongo import MongoClient

if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
    print("Configuring mongodb to connect to mongo-server docker")
    client=MongoClient('mongo-server',27017)
else:
    print("Configuring mongodb to connect to localhost")
    client=MongoClient()

mongodb_db=client['setchks_app']


################################
################################
# Simple health check endpoint #
################################
################################

@bp.route("/healthy")
def health_check():
    logger.info("health check called")
    return "Healthy"

#####################################
#####################################
##     data upload endpoint        ##
#####################################
#####################################

@bp.route('/data_upload', methods=['GET','POST'])
def data_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    bc=Breadcrumbs()
    bc.set_current_page("data_upload")

    return render_template('data_upload.html',
                           setchks_session=setchks_session,
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                            )

#####################################
#####################################
##     confirm upload endpoint     ##
#####################################
#####################################


@bp.route('/confirm_upload', methods=['GET','POST'])
def confirm_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    # if reach here via file upload, load the data into matrix
    if 'uploaded_file' in request.files:
        setchks_session.load_data_into_matrix(data=request.files['uploaded_file'], upload_method='from_text_file', table_has_header=True)
        setchks_session.setchks_results={} # throw away all old results
        session['setchks_session']=setchks_session # save updated setchks_session to the session variable

    else:
        pass

    bc=Breadcrumbs()
    bc.set_current_page(current_page_name="confirm_upload")

    return render_template('confirm_upload.html',
                           setchks_session=setchks_session,
                           file_data=setchks_session.data_as_matrix,
                           filename=setchks_session.filename,
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                            )

#####################################
#####################################
##    column identities endpoint   ##
#####################################
#####################################

@bp.route('/column_identities', methods=['GET','POST'])
def column_identities():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    
    if setchks_session.columns_info==None:
        ci=ColumnsInfo(ncols=len(setchks_session.data_as_matrix[0]))
        ci.set_column_type(icol=0,requested_column_type="CID")
        ci.set_column_type(icol=1,requested_column_type="DTERM")
        setchks_session.columns_info=ci

    # if reach here via click on versions pulldown
    if len(request.form.keys())!=0:
       k, v=list(request.form.items())[0]
       print("===>>>>", k, v)
       # col_label is of form e.g. type_selector_for_col_3
       icol=int(k.split("_")[-1])
       requested_column_type=v
       ci=setchks_session.columns_info
       success_flag, message=ci.set_column_type(icol=icol,requested_column_type=requested_column_type)
       logger.debug("Type change attempt: %s %s %s %s" % (icol, requested_column_type, success_flag, message))
       print(ci.column_types)
       print(ci.identified_columns)
    #    setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['select_sct_version'])-1]

    setchks_session.marshalled_rows=[]
    for row in setchks_session.data_as_matrix[setchks_session.first_data_row:]:
        mr=MarshalledRow(row_data=row, columns_info=setchks_session.columns_info)
        setchks_session.marshalled_rows.append(mr)

    type_labels={"CID":"Concept Id", "DID":"Description Id", "MIXED":"Mixed Id", "DTERM":"Term","OTHER":"Other"}
    column_type_labels=[type_labels[x] for x in setchks_session.columns_info.column_types]

    rows_processable=[mr.row_processable for mr in setchks_session.marshalled_rows]
    logger.debug("rows_processable:"+str(rows_processable))

    bc=Breadcrumbs()
    bc.set_current_page("column_identities")

    return render_template('column_identities.html',
                           setchks_session=setchks_session,
                           file_data=setchks_session.data_as_matrix,
                           filename=setchks_session.filename,
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                           rows_processable=rows_processable,
                           column_type_labels=column_type_labels,
                            )

#####################################
#####################################
##     enter metadata endpoint     ##
#####################################
#####################################

@bp.route('/enter_metadata', methods=['GET','POST'])
def enter_metadata():
    print("ENTER METADATA FORM KEYS", request.form.keys())
    print("ENTER METADATA DATA", request.data)
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)
 
    if setchks_session.available_sct_versions is None:
        setchks_session.available_sct_versions=get_sct_versions.get_sct_versions()
        setchks_session.sct_version=setchks_session.available_sct_versions[0]

    # if reach here via click on versions pulldown
    if 'select_sct_version' in request.form:
        print("===>>>>", request.form['select_sct_version'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['select_sct_version'])-1]
    
    # if reach here via click on versions timeline
    if 'pointNumber' in request.form:
        print("===>>>>", request.form['pointNumber'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['pointNumber'])]
    
    timeline_data_json, timeline_layout_json, timeline_info_json=graphical_timeline.create_graphical_timeline(
        selected_sct_version=setchks_session.sct_version,
        available_sct_versions=setchks_session.available_sct_versions,
        )
    
    bc=Breadcrumbs()
    bc.set_current_page("enter_metadata")

    return render_template(
        'enter_metadata.html',
        breadcrumbs_styles=bc.breadcrumbs_styles,
        setchks_session=setchks_session,
        timeline_data_json=timeline_data_json,
        timeline_layout_json=timeline_layout_json,
        timeline_info_json=timeline_info_json,
        )

#############################################
#############################################
##     select and run checks  endpoint     ##
#############################################
#############################################

@bp.route('/select_and_run_checks', methods=['GET','POST'])
def select_and_run_checks():
    print("ENTER METADATA FROM KEYS", request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    bc=Breadcrumbs()
    bc.set_current_page("select_and_run_checks")

    if setchks_session.selected_setchks==None:
        setchks_session.selected_setchks=available_setchks

    if "run_checks" in request.args:
        setchks_to_run=[ setchks_app.setchks.setchk_definitions.setchks[x] for x in setchks_session.selected_setchks]
        logger.debug(str(setchks_to_run))
        setchks_session.setchks_jobs_list=setchks_app.setchks.run_queued_setchks.run_queued_setchks(setchks_list=setchks_to_run, setchks_session=setchks_session)

    if "download_report" in request.args:
        logger.debug("Report requested")
        user_tmp_folder="/tmp/"+setchks_session.uuid
        os.system("mkdir -p " + user_tmp_folder)
        excel_filename="%s/setchks_output_%s.xlsx" % (user_tmp_folder,  datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S'))
        setchks_session.generate_excel_output(excel_filename=excel_filename)
        return send_file(excel_filename)

    results_available=len(list(setchks_session.setchks_results)) > 0

    return render_template('select_and_run_checks.html',
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                           setchks_session=setchks_session,
                           results_available=results_available,
                           all_setchks=setchks_app.setchks.setchk_definitions.setchks,
                            )