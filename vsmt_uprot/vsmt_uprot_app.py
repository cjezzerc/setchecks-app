import time
import sys
import os
import os.path
import requests
import pprint
import time

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils

import vsmt_uprot.terminology_server_module
import vsmt_uprot.vsmt_valueset


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.exceptions import abort

bp = Blueprint('vsmt_uprot_app', __name__)

#######################################################
# For now have one single global persistence filename #
#######################################################

# quick and dirty storage for the ecl expansions between endpoint calls
expansion_store={}
ecl_store=[]
refset_store=[]
terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url="https://dev.ontology.nhs.uk/dev1/fhir/",
                    auth_url="https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token")
# sct_version="http://snomed.info/sct/83821000000107/version/20190807"
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
    global ecl_store # must find better way to implement this

    if 'ecl' in request.form:
        ecl=request.form['ecl']
        ecl_response=terminology_server.do_expand(ecl=ecl, sct_version=sct_version, add_display_names=True)
        if ecl_response is not None: 
            ecl_store = [ecl] + ecl_store
            ecl_response=["%s concept(s):" % (len(ecl_response))] + ecl_response
        else:
            ecl_store = ["ERROR:  "+ecl] + ecl_store
            ecl_response=["There was an error in the ECL:", response.json()]
    else:
        ecl='Enter your ECL here'
        ecl_response=['Response of ECL evaluation will appear here']

    return render_template('ecl_explorer.html',
                            ecl=ecl,
                            ecl_response=ecl_response,
                            ecl_store=ecl_store
                            )

#####################################
#####################################
##     refset_members endpoint     ##
#####################################
#####################################

@bp.route('/refset_members', methods=['GET','POST'])
def refset_members():
    global refset_store # must find better way to implement this

    if 'refset_id' in request.form:
        refset_id=request.form['refset_id'].strip()
        refset_response=terminology_server.do_expand(refset_id=refset_id, sct_version=sct_version, add_display_names=True)
        if refset_response is not None: 
            refset_store = [refset_id] + refset_store
            refset_response=["%s concept(s):" % (len(refset_response))] + refset_response
        else:
            refset_store = ["ERROR:  "+refset_id] + refset_store
            refset_response=["There was an error for refset:", refset_response.json()]
    else:
        refset_id='Enter refset_id here'
        refset_response=['Response of refset evaluation will appear here']

    return render_template('refset_members.html',
                            refset_id=refset_id,
                            refset_response=refset_response,
                            refset_store=refset_store
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

    if current_vs_enum not in list(vsmt_index.keys()): # default back to 0 if new list since last rendering (need to fi logic better here)
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

    sct_version1="http://snomed.info/sct/83821000000107/version/" + "20200415"
    expansion1=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version1)
    
    sct_version2="http://snomed.info/sct/83821000000107/version/" + "20200805"
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
                            only_in_2=only_in_2
,                            )