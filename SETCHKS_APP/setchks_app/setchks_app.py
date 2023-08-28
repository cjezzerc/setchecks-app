import os
import os.path
import sys

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
import vsmt_uprot.setchks.setchks_session
import vsmt_uprot.setchks.setchk_definitions 
from vsmt_uprot.setchks.data_as_matrix.columns_info import ColumnsInfo
from vsmt_uprot.setchks.data_as_matrix.marshalled_row_data import MarshalledRow


from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.gui import gui_setchks_session

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.exceptions import abort

bp = Blueprint('setchks_app', __name__)


from pymongo import MongoClient

# Consider this section again if and when hook up to mongodb
# if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
#     print("Configuring mongodb to connect to mongo-server docker")
#     client=MongoClient('mongo-server',27017)
# else:
#     print("Configuring mongodb to connect to localhost")
#     client=MongoClient()

# db=client['setchks_app']


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
                           file_data=setchks_session.data_as_matrix,
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
        
        # print(setchks_session)
        session['setchks_session']=setchks_session # save updated setchks_session to the session variable
    else:
        pass

    bc=Breadcrumbs()
    bc.set_current_page(current_page_name="confirm_upload")

    return render_template('confirm_upload.html',
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

    ci=ColumnsInfo(ncols=len(setchks_session.data_as_matrix[0]))
    ci.set_column_type(icol=0,requested_column_type="CID")
    ci.set_column_type(icol=1,requested_column_type="DTERM")
    setchks_session.columns_info=ci

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
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    from fhir.resources.bundle import Bundle

    terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                        auth_url=os.environ["ONTOAUTH_INSTANCE"])
    relative_url= "CodeSystem?url=http://snomed.info/sct"
    response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
    bundle=Bundle.parse_obj(response.json())
    sct_versions=[be.resource.dict()["version"] for be in bundle.entry]

    bc=Breadcrumbs()
    bc.set_current_page("enter_metadata")

    return render_template('enter_metadata.html',
                           breadcrumbs_styles=bc.breadcrumbs_styles,
                           sct_versions=sct_versions,
                            )