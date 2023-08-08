import time
import sys
import os
import os.path
import requests
import pprint
import time
import bson

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils

import vsmt_uprot.terminology_server_module
import vsmt_uprot.vsmt_valueset
import vsmt_uprot.setchks.setchks_session
import vsmt_uprot.setchks.setchk_definitions 


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.exceptions import abort

bp = Blueprint('vsmt_uprot_app', __name__)

#######################################################
# For now have one single global persistence filename #
#######################################################

from pymongo import MongoClient

# client=MongoClient()
#
# client = MongoClient('mongodb://172.17.0.0/16:27017/')
# client = MongoClient("mongodb://172.17.0.0/16", 27017)

# temp fix: uncomment one of these
if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
    print("Configuring mongodb to connect to mongo-server docker")
    client=MongoClient('mongo-server',27017)
else:
    print("Configuring mongodb to connect to localhost")
    client=MongoClient()


db=client['VSMT_uprot_app']
ecl_history=db['ecl_histories'].find_one()
if ecl_history is None:
    db['ecl_histories'].insert_one({"ecl_store":[]})
refset_history=db['refset_histories'].find_one()
print("REFSET_HISTORY", refset_history)
if refset_history is None:
    db['refset_histories'].insert_one({"refset_store":[]})


terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
sct_version=None


################################
################################
# Simple health check endpoint #
################################
################################

@bp.route("/healthy")
def health_check():
    return "Healthy"

#####################################
#####################################
##     ecl explorer endpoint       ##
#####################################
#####################################

@bp.route('/ecl_explorer', methods=['GET','POST'])
def ecl_explorer():
   
    ecl_history=db.ecl_histories.find_one()  # there is only one while single user mode
    if 'ecl' in request.form:
        
        ecl=request.form['ecl']
        terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
        ecl_response=terminology_server.do_expand(ecl=ecl, sct_version=sct_version, add_display_names=True)
        if ecl_response is not None: 
            # ecl_store = [ecl] + ecl_store
            ecl_history['ecl_store'] = [ecl] + ecl_history['ecl_store']
            ecl_response=["%s concept(s):" % (len(ecl_response))] + ecl_response
        else:
            # ecl_store = ["ERROR:  "+ecl] + ecl_store
            ecl_history['ecl_store'] = ["ERROR:  "+ecl] + ecl_history['ecl_store']
            ecl_response=["There was an error in the ECL:", response.json()]
        db.ecl_histories.replace_one({"_id":ecl_history['_id']}, ecl_history)
    else:
        ecl='Enter your ECL here'
        ecl_response=['Response of ECL evaluation will appear here']

    return render_template('ecl_explorer.html',
                            ecl=ecl,
                            ecl_response=ecl_response,
                            ecl_store=ecl_history['ecl_store']
                            )

#####################################
#####################################
##     refset_members endpoint     ##
#####################################
#####################################

@bp.route('/refset_members', methods=['GET','POST'])
def refset_members():

    refset_history=db.refset_histories.find_one()  # there is only one while single user mode
    print(refset_history)
    if 'refset_id' in request.form:
        refset_id=request.form['refset_id'].strip()
        refset_response=terminology_server.do_expand(refset_id=refset_id, sct_version=sct_version, add_display_names=True)
        if refset_response is not None: 
            refset_history['refset_store'] = [refset_id] + refset_history['refset_store']
            refset_response=["%s concept(s):" % (len(refset_response))] + refset_response
        else:
            refset_history['refset_store'] = ["ERROR:  "+refset_id] + refset_history['refset_store']
            refset_response=["There was an error for refset:", refset_response.json()]
    else:
        refset_id='Enter refset_id here'
        refset_response=['Response of refset evaluation will appear here']
    db.refset_histories.replace_one({"_id":refset_history['_id']}, refset_history)
    return render_template('refset_members.html',
                            refset_id=refset_id,
                            refset_response=refset_response,
                            refset_store=refset_history['refset_store']
                            )

#####################################
#####################################
##     vsmt index endpoint         ##
#####################################
#####################################


@bp.route('/vsmt_index', methods=['GET'])
def vsmt_index():

    print(request.args)

    ######################################
    # Determine current_vs_enum either   #
    # i) as in URL                       # 
    # ii) as currently set in cookie     #
    # iii) otherwise default to 0        # 
    ######################################
    
    print("REQUEST:",request.args)

    if "vs_enum" in request.args:
        requested_vs_enum=int(request.args["vs_enum"])
    else:
        requested_vs_enum=None

    if requested_vs_enum is not None: # use requested id if it specified in URL
        current_vs_enum=requested_vs_enum
    else:
        if 'current_vs_enum' in session.keys(): # otherwise if current id already stored in session cookie use that 
            current_vs_enum=session['current_vs_enum']
        else:
            current_vs_enum=0 # otherwise default to 0
    
    session['current_vs_enum']=current_vs_enum
    session.modified=True

    terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
    value_set_manager=vsmt_uprot.vsmt_valueset.VSMT_ValueSetManager(terminology_server=terminology_server)
    vsmt_index=value_set_manager.get_vsmt_index_data()

    if current_vs_enum >= len(list(vsmt_index.keys())): # default back to 0 if new list since last rendering (need to fi logic better here)
        current_vs_enum=0 
    current_index_key=list(vsmt_index.keys())[current_vs_enum]
    print(current_vs_enum, current_index_key)

    session['current_index_key']=current_index_key
    session.modified=True

    vs=vsmt_uprot.vsmt_valueset.VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=current_index_key)
    includes=vs.get_includes()
    excludes=vs.get_excludes()
    top_level_annotation=vs.get_top_level_annotation()
    
    return render_template('vsmt_index.html',
                            vsmt_index=vsmt_index,
                            current_index_key=current_index_key,
                            includes=includes,
                            excludes=excludes,
                            top_level_annotation=top_level_annotation,
                            )


#####################################
#####################################
##     expansion endpoint          ##
#####################################
#####################################


@bp.route('/expansion', methods=['GET'])
def expansion():

    current_index_key=session['current_index_key']
    terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
    vs=vsmt_uprot.vsmt_valueset.VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=current_index_key)

    sct_version="http://snomed.info/sct/83821000000107/version/" + "20200415"
    # expansion=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version)
    expansion=vs.expand_version_on_server(add_display_names=True, sct_version=None)

    print("==>", vs.get_vsmt_identifier_and_version())
    return render_template('vsmt_expansion.html',
                            vs=vs,
                            expansion=expansion,
                            )

#####################################
#####################################
##     diff endpoint               ##
#####################################
#####################################


@bp.route('/diff', methods=['GET'])
def diff():

    current_index_key=session['current_index_key']
    terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
    vs=vsmt_uprot.vsmt_valueset.VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=current_index_key)

    # sct_version1="http://snomed.info/sct/83821000000107/version/" + "20220511"
    sct_version1="http://snomed.info/sct/83821000000107/version/" + "20230315"
    expansion1=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version1)
    
    sct_version2="http://snomed.info/sct/83821000000107/version/" + "20230412"
    # sct_version2="http://snomed.info/sct/83821000000107/version/" + "20230315"
    expansion2=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version2)

    only_in_1=[]
    in_both=[]
    for concept in expansion1:
        if concept not in expansion2:
            only_in_1.append(concept)
        else:
            in_both.append(concept)
    
    only_in_2=[]
    for concept in expansion2:
        if concept not in expansion1:
            only_in_2.append(concept)

    print("==>", len(only_in_1), len(only_in_2))

    return render_template('vsmt_diff.html',
                            vs=vs,
                            sct_version1=sct_version1,
                            sct_version2=sct_version2,
                            in_both=in_both,
                            only_in_1=only_in_1,
                            only_in_2=only_in_2,
                            )


#####################################
#####################################
##     trial upload endpoint       ##
#####################################
#####################################


@bp.route('/trial_upload', methods=['GET','POST'])
def trial_upload():
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 

    if 'myfile' in request.files:
        setchks_session.load_uploaded_data_into_matrix(data=request.files['myfile'], upload_method='from_text_file', table_has_header=True)
        print(setchks_session)
        session['setchks_session']=setchks_session # save updated setchks_session to the session variable
    else:
        pass

    return render_template('trial_upload.html',
                           file_data=setchks_session.data_as_matrix
                            )

#####################################
#####################################
##     CHK06_DEF_EXCL_FILTER       ##
#####################################
#####################################


@bp.route('/CHK06_DEF_EXCL_FILTER', methods=['GET','POST'])
def do_CHK06_DEF_EXCL_FILTER():
    

    setchk=vsmt_uprot.setchks.setchk_definitions.setchks['CHK06_DEF_EXCL_FILTER']

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 

    setchks_session.terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                        auth_url=os.environ["ONTOAUTH_INSTANCE"])

    release_label="20230412"
    setchks_session.sct_version="http://snomed.info/sct/83821000000107/version/" + release_label

    setchks_session.cid_col=0

    print("=====================")
    setchk.run_check(setchks_session=setchks_session)
    print("=====================")

    print("++++++++++++++++++++++++")
    print("After set check ran, setchks_sessions is:")
    print(setchks_session)
    print("++++++++++++++++++++++++")

    print("++++++++++++++++++++++++")
    for k,v in setchks_session.setchks_results.items(): 
        print("Results for check %s :" % k)
        print(v)
    print("++++++++++++++++++++++++")

    results=setchks_session.setchks_results["CHK06_DEF_EXCL_FILTER"]
    n_set_members_in_refset=results.set_analysis["n_set_members_in_refset"]
    row_results=results.row_analysis
    row_messages=[x["Message"] for x in row_results]
    set_message=results.set_analysis["Message"]

    return render_template('CHK06_DEF_EXCL_FILTER.html',
                           file_data=setchks_session.data_as_matrix,
                           row_messages=row_messages,
                           set_message=set_message,
                            )
