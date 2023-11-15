import os
import os.path
import sys
import copy
import datetime
import boto3
import json
import jsonpickle
from flask import jsonify

import logging
logger=logging.getLogger(__name__)

location=os.path.abspath(os.getcwd())
print(location)
sys.path.append(location+"/../VSMT_UPROT_APP/")

from fhir.resources.valueset import ValueSet

import setchks_app.setchks.setchks_session
import setchks_app.setchks.setchk_definitions 
import setchks_app.setchks.run_queued_setchks

from setchks_app.data_as_matrix.columns_info import ColumnsInfo
from setchks_app.data_as_matrix.marshalled_row_data import MarshalledRow
from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.concepts_service.concepts_service import ConceptsService

from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.gui import gui_setchks_session
from setchks_app.sct_versions import get_sct_versions
from setchks_app.sct_versions import graphical_timeline
from setchks_app.mongodb import get_mongodb_client
from setchks_app.redis.rq_utils import get_rq_info, launch_sleep_job, jobs, job_result, job_stack_trace, report_on_env_vars, launch_report_on_env_vars
from rq import Queue
from setchks_app.redis.get_redis_client import get_redis_string, get_redis_client

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app, send_file,
)
from werkzeug.exceptions import abort

bp = Blueprint('setchks_app', __name__)

# This list should probably come from a config file in due course
available_setchks=[
    'CHK20_INCORR_FMT_SCTID', 
    'CHK02_IDS_IN_RELEASE', 
    'CHK01_APPROP_SCTID', 
    'CHK06_DEF_EXCL_FILTER',
    'CHK05_UNRECC_HIERARCH',
    'CHK04_INACTIVES_ENTRY',
    'CHK10_MISSING_CONCEPTS',
    'CHK14_MANY_CLAUSES',
    ]

# from pymongo import MongoClient

# if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
#     print("Configuring mongodb to connect to mongo-server docker")
#     client=MongoClient('mongo-server',27017)
# else:
#     print("Configuring mongodb to connect to localhost")
#     client=MongoClient()

# mongodb_db=client['setchks_app']

################################
################################
# Simple health check endpoint #
################################
################################

@bp.route("/healthy")
def health_check():
    logger.info("health check called")
    return "Healthy"

#################################
#################################
# Simple redis endpoint #
#################################
#################################

@bp.route("/redis_check")
def redis_check():
    logger.debug("redis check called (with ssl=True)")
    
    import redis

    if os.environ["DEPLOYMENT_ENV"]=="AWS":
        redis_connection=get_redis_string()
    else:
        redis_host="localhost"

    logger.debug(f"redis_host = {redis_host}")

    if os.environ["DEPLOYMENT_ENV"]=="AWS":
        redis_connection = redis.Redis(host=redis_host, port=6379, decode_responses=True, ssl=True)
    else: # so not really an SSL test if going to localhost (otherwise it does hang to localhost)
        redis_connection = redis.Redis(host=redis_host, port=6379, decode_responses=True, ssl=False)

    logger.debug(f"redis_connection = {redis_connection}")
    
    logger.debug(f"about to do ping..")
    redis_ping=redis_connection.ping()
    logger.debug(f"..ping result is {redis_ping}")

    logger.debug(f"about to do set..")
    redis_connection.set('mykey', str(datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S')))
    logger.debug(f"..done set")

    logger.debug(f"about to do get..")
    time_value=redis_connection.get('mykey')
    logger.debug(f"..done get")

    return f"redis check:_____{redis_ping}______{time_value}"


#################################
#################################
#   Simple session endpoint     #
#################################
#################################

@bp.route("/session_check")
def session_check():
    logger.info("session check called")
    session['time']=str(datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S'))
    return f"session contents:{session.items()}"

#################################
#################################
# Simple mongodb check endpoint #
#################################
#################################

@bp.route("/mongodb_check")
def mongodb_check():
    logger.info("mongodb check called")

    mongodb_client=get_mongodb_client.get_mongodb_client()
    collection=mongodb_client["mongodb_check"]["mongodb_check"]
    logger.info("mongodb connection to db made")
    collection.insert_one({"insert_time": datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S')})
    logger.info("inserted document")
    output_strings=["Collection 'mongodb check' contents:"]
    for doc in collection.find():
        output_strings.append(str(doc))
    output_strings.append("/nDatabase contents:")
    for db_name in mongodb_client.list_database_names():
        db=mongodb_client[db_name]
        logger.debug("db_name")
        for c_name in db.list_collection_names():
            logger.debug("db_name"+"-"+c_name)
            c=db[c_name]
            # n_documents=c.estimated_document_count() # does not seem to work in DocumentDB
            #  n_documents=c.count_documents({}) # horribly slow on ig tables
            # output_strings.append(f'db: {db_name:30s} collection:{c_name:30s} est_n_documents:{n_documents}')                
            output_strings.append(f'db: {db_name:30s} collection:{c_name:30s}')                

    return '<br>'.join(output_strings)


#################################
#################################
# manipulate descriptions db    #
#################################
#################################

@bp.route("/descriptions_db")
def descriptions_db():
    logger.info("descriptions_db called")
    logger.debug(list(request.args.items()))
    action=request.args.get("action", None)
    date_string=request.args.get("date_string", None)
    data_type=request.args.get("data_type", "descriptions") # alternatives are "hst" or "qt" though "qt" not used currently
    if data_type=="concepts":
      ds=ConceptsService()
    else:
      ds=DescriptionsService(data_type=data_type)

    if action=="list":
        output_strings=[f"db '{data_type}' contents:"]
        for c_name in ds.db.list_collection_names():
            logger.debug("db_name"+"-"+c_name)
            output_strings.append(f'collection:{c_name:30s}')                
        return '<br>'.join(output_strings)
    
    if action=="drop":
        collection_name=ds.make_collection_name(date_string=date_string)
        collection=ds.db[collection_name]
        collection.drop()
        return f"Dropped {collection_name}"
    
    if action=="describe_collection":
        collection_name=ds.make_collection_name(date_string=date_string)
        collection=ds.db[collection_name]
        output_strings=[f"Information for collection with date_string: {date_string}"]
        output_strings.append(f"Number of documents : {collection.count_documents({})}")
        output_strings.append(f"Index information : {collection.index_information()}")
        return "<br>".join(output_strings)
    
    if action=="make":
        redis_connection=get_redis_client()
        q = Queue(connection=redis_connection)
        result = q.enqueue(ds.pull_release_from_trud, job_timeout='15m', date_string=date_string)
        result=str(result)[1:-1]
        logger.debug(f'result={result}')
        return f'jobid={result}'
    
    if action=="make_missing":
        redis_connection=get_redis_client()
        q = Queue(connection=redis_connection)
        result = q.enqueue(ds.make_missing_collections, job_timeout='24h')
        result=str(result)[1:-1]
        logger.debug(f'result={result}')
        return f'jobid={result}'
    
    if action=="check_coverage":
        redis_connection=get_redis_client()
        result = ds.check_whether_releases_on_ontoserver_have_collections()
        output_strings=[f'{x}:{result[x]}' for x in result]
        return "<br>".join(output_strings)
    

    return f"Did not understand that"


#####################################
#####################################
##     rq endpoint                 ##
#####################################
#####################################

@bp.route("/rq")
def rq():
    logger.info("rq called")
    logger.debug(list(request.args.items()))
    action=request.args.get("action", None)
    job_id=request.args.get("job_id", None)
    
    if action is None:
        output_strings=get_rq_info()
        return '<br>'.join(output_strings)
    
    if action =="launch_sleep_job":
        result=launch_sleep_job()
        result=str(result)[1:-1]
        logger.debug(f'result={result}')
        return result
    
    if action=="app_ev":
        return '<pre>'+'<br>'.join(report_on_env_vars())+'</pre>'
    
    if action=="worker_ev":
        launch_report_on_env_vars()
        return 'Look in logs for output'

    if action =="jobs":
        # return str(jobs())
        return '<pre>'+'<br>'.join(jobs())+'</pre>'
    
    if action=="job_stack_trace":
        return '<pre>'+'<br>'.join(job_stack_trace(job_id=job_id))+'</pre>'
    
    if action=="job_result":
        return '<pre>'+str(job_result(job_id=job_id))+'</pre>'
    
    if action=="setchk_job_result":
        return str(job_result(job_id=job_id).__repr__())
        # return jsonify(json.loads(jsonpickle.encode(job_result(job_id=job_id), unpicklable=False)))
    
    return f"Did not understand that: {action}"

#####################################
#####################################
##     data upload endpoint        ##
#####################################
#####################################

@bp.route('/', methods=['GET'])
@bp.route('/data_upload', methods=['GET','POST'])
def data_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)
    print(f"session keys={list(session.keys())}")

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
        setchks_session.load_data_into_matrix(data=request.files['uploaded_file'], upload_method='from_file', table_has_header=True)
        setchks_session.reset_analysis() # throw away all old results
        setchks_session.marshalled_rows=[]
        # session['setchks_session']=setchks_session # save updated setchks_session to the session variable

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

    # set column_info if nor already set OR data has changed number of columns (allows simple reload to leave it unchanged) 
    if (setchks_session.columns_info==None) or (setchks_session.columns_info.ncols != len(setchks_session.data_as_matrix[0])):
        ci=ColumnsInfo(ncols=len(setchks_session.data_as_matrix[0]))
        ci.set_column_type(icol=0,requested_column_type="MIXED")
        ci.set_column_type(icol=1,requested_column_type="DTERM")
        setchks_session.columns_info=ci

    # if reach here via click on versions pulldown
    if len(request.form.keys())!=0:
        k, v=list(request.form.items())[0]
        # print("===>>>>", k, v)
        # col_label is of form e.g. type_selector_for_col_3
        icol=int(k.split("_")[-1])
        requested_column_type=v
        ci=setchks_session.columns_info
        success_flag, message=ci.set_column_type(icol=icol,requested_column_type=requested_column_type)
        logger.debug("Type change attempt: %s %s %s %s" % (icol, requested_column_type, success_flag, message))
        if success_flag: # if have changed column types (in any way)
            setchks_session.reset_analysis() # throw away all old results
            setchks_session.marshalled_rows=[] # force recalc of marshalled rows

    if setchks_session.marshalled_rows==[]:
        for row in setchks_session.data_as_matrix[setchks_session.first_data_row:]: # The marshalled_rows list does NOTinclude the header row
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

    current_sct_version=setchks_session.sct_version # remember this in case changes in next sections

    # if reach here via click on versions pulldown
    if 'select_sct_version' in request.form:
        # print("===>>>>", request.form['select_sct_version'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['select_sct_version'])-1]
    
    # if reach here via click on versions timeline
    if 'pointNumber' in request.form:
        # print("===>>>> pointNumber=", request.form['pointNumber'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['pointNumber'])]

    if 'data_entry_extract_type' in request.form:
        # print("===>>>>", request.form['data_entry_extract_type'])
        setchks_session.data_entry_extract_type=request.form['data_entry_extract_type']
        setchks_session.reset_analysis() # throw away all old results


    if setchks_session.sct_version!=current_sct_version: # if have changed sct_version
        setchks_session.reset_analysis() # throw away all old results

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

    setchks_jobs_manager=setchks_session.setchks_jobs_manager
    if setchks_jobs_manager is not None:
        job_status_report=setchks_jobs_manager.update_job_statuses()
        logger.debug("\n".join(job_status_report))

    if (
        "run_checks" in request.args 
        and (
             setchks_jobs_manager is None
             or setchks_jobs_manager.jobs_running==False 
             )
        ):
        if setchks_session.setchks_results=={}: # Missing results means either 
                                                # marshalled rows never calculated, 
                                                # or sct_release or column_identities have changed
            for mr in setchks_session.marshalled_rows:
                mr.do_things_dependent_on_SCT_release(setchks_session=setchks_session)


            
        setchks_to_run=[]
        for sc in setchks_session.selected_setchks: # really the logic in next two lines should be applied when 
                                                    # creating/amending selected_setchks list - change when implement that
            this_setchk = setchks_session.available_setchks[sc]
            if ("ALL" in this_setchk.setchk_data_entry_extract_types or 
                setchks_session.data_entry_extract_type in this_setchk.setchk_data_entry_extract_types
                ):
                setchks_to_run.append(this_setchk)
                print("YES -", sc)
            else:
                print("NO -", sc)

        # setchks_to_run=[ setchks_app.setchks.setchk_definitions.setchks[x] for x in setchks_session.selected_setchks]
        logger.debug(str(setchks_to_run))
        setchks_session.setchks_jobs_list=setchks_app.setchks.run_queued_setchks.run_queued_setchks(
            setchks_list=setchks_to_run, 
            setchks_session=setchks_session
            )

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

#############################################
#############################################
##     report setchks_session  endpoint    ##
#############################################
#############################################

@bp.route('/setchks_session', methods=['GET'])
def setchks_session():
    
    setchks_session=gui_setchks_session.get_setchk_session(session)

    # surely there has to be a simplification to the line below!
    return jsonify(json.loads(jsonpickle.encode(setchks_session, unpicklable=False)))

#############################################
#############################################
##     hard reset endpoint    ##
#############################################
#############################################

@bp.route('/reset_setchks_session', methods=['GET'])
def reset_setchks_session():
    session['setchks_session']=None
    return redirect("/data_upload")

#############################################
#############################################
##     report refactored form  endpoint    ##
#############################################
#############################################

@bp.route('/refactored_form', methods=['GET'])
def refactored_form():
    from setchks_app.set_refactoring.concept_module import ConceptsDict
    setchks_session=gui_setchks_session.get_setchk_session(session)
    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)
    output_strings=["Refactored form:"]
    for clause in setchks_session.refactored_form.clause_based_rule.clauses:
        pt=concepts[str(clause.clause_base_concept_id)].pt
        output_strings.append(f"{clause.clause_type} {clause.clause_operator:2} {str(clause.clause_base_concept_id):20} {pt}")
    return_string="<pre>"+"<br>".join(output_strings)+"</pre>"
    # surely there has to be a simplification to the line below!
    return return_string

######################################
######################################
## path validaotr endpoint endpoint ##
######################################
######################################

@bp.route('/', methods=['GET'])
@bp.route('/path_validator', methods=['GET','POST'])
def path_validator():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)
    import requests, pprint
    data_to_show="No data yet"
    if 'uploaded_file' in request.files:
        # ofh=open("/tmp/path_validator.json","wb")
        filename=getattr(request.files['uploaded_file'],'filename',None)
        file_data=request.files['uploaded_file'].read()
        if filename[-4:]==".xml":
            file_type="xml"
        else:
            file_type="json"
        # ofh.write(data)
        # ofh.close()

        profile="https://fhir.hl7.org.uk/StructureDefinition/UKCore-Bundle"
        url=f'https://3cdzg7kbj4.execute-api.eu-west-2.amazonaws.com/poc/Conformance/FHIR/R4/$validate?profile={profile}'
        # url=f'https://3cdzg7kbj4.execute-api.eu-west-2.amazonaws.com/poc/Conformance/FHIR/R4/$validate'

        # json_data=open(filename).read()
        

        headers={}
        if file_type=="json":
            dict_data=json.loads(file_data)
            headers["accept"]="application/fhir+json"
            headers["Content-Type"]="application/fhir+json"
            r=requests.post(url=url, json=dict_data, headers=headers)
        else:
            # print(file_data.decode())
            # dict_data=json.loads(file_data.decode())
            headers["accept"]="application/fhir+xml"
            headers["Content-Type"]="application/fhir+xml"
            r=requests.post(url=url, json=file_data.decode(), headers=headers)

        
        
        data_to_show="<pre>"+"<br>".join(pprint.pformat(r.json()).split('\n'))+"</pre>"
        # data_to_show=r.json()


    return render_template('path_validator.html',
                            data_to_show=data_to_show
                            )