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
##     simple endpoint             ##
#####################################
#####################################

@bp.route('/ecl_explorer', methods=['GET','POST'])
def ecl_explorer():
    global ecl_store # must find better way to implement this

    if 'ecl' in request.form:
        ecl=request.form['ecl']
        ecl_response=terminology_server.expand_ecl(ecl=ecl, sct_version=sct_version, add_display_names=True)
        if ecl_response is not None: 
            ecl_store = [ecl] + ecl_store
            ecl_response=["%s concept(s):" % (len(ecl_response))] + ecl_response
        else:
            ecl_store = ["ERROR:  "+ecl] + ecl_store
            ecl_response=["There was an error in the ECL:", response.json()]
    else:
        ecl='Enter your ECL here'
        ecl_response=['Response of ECL evaluation will appear here']

    return render_template('simple.html',
                            ecl=ecl,
                            ecl_response=ecl_response,
                            ecl_store=ecl_store
                            )


