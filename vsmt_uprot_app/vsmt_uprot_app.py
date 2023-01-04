import time
import sys
import os
import os.path
import requests
import pprint
import time

from fhir.resources.valueset import ValueSet
import vsmt_uprot_app.fhir_utils

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
        url='https://r4.ontoserver.csiro.au/fhir/ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=ecl/(%s)' % ecl
        print(url)
        response=requests.get(url=url)
        if response.json()["resourceType"]=="ValueSet": # if get a valid response store ecl for later reuse
            ecl_store = [ecl] + ecl_store
            extensional_valueset=ValueSet.parse_obj(response.json())
            ecl_response=[]
            ecl_response.append("%s concept(s):" % (extensional_valueset.expansion.total))
            if extensional_valueset.expansion.contains:
                for contained_item in extensional_valueset.expansion.contains:
                    ecl_response.append("%20s | %s |" % (contained_item.code, contained_item.display))
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


