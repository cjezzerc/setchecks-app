import time
import sys
import os
import os.path
import requests
import pprint
import time

from fhir.resources.valueset import ValueSet
import vsmt_uprot_app.fhir_utils

import vsmt_uprot_app.terminology_server_module
import vsmt_uprot_app.vsmt_valueset

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
terminology_server=vsmt_uprot_app.terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
sct_version="http://snomed.info/sct/83821000000107/version/20190807"


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

    terminology_server=vsmt_uprot_app.terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    value_set_manager=vsmt_uprot_app.vsmt_valueset.VSMT_ValueSetManager(terminology_server=terminology_server)
    vsmt_index=value_set_manager.get_vsmt_index_data()

    current_index_key=list(vsmt_index.keys())[current_vs_enum]
    print(current_vs_enum, current_index_key)

    session['current_index_key']=current_index_key
    session.modified=True

    vs=vsmt_uprot_app.vsmt_valueset.VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=current_index_key)
    includes=vs.get_includes()
    excludes=vs.get_excludes()
    
    return render_template('vsmt_index.html',
                            vsmt_index=vsmt_index,
                            current_index_key=current_index_key,
                            includes=includes,
                            excludes=excludes,
                            )


#####################################
#####################################
##     expansion endpoint          ##
#####################################
#####################################


@bp.route('/expansion', methods=['GET'])
def expansion():

    current_index_key=session['current_index_key']
    terminology_server=vsmt_uprot_app.terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    vs=vsmt_uprot_app.vsmt_valueset.VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=current_index_key)

    sct_version="http://snomed.info/sct/83821000000107/version/" + "20200415"
    expansion=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version)

    print("==>", vs.get_vsmt_identifier_and_version())
    return render_template('vsmt_expansion.html',
                            vs=vs,
                            expansion=expansion,
                            )