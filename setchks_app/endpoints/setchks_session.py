#############################################
#############################################
##     report setchks_session  endpoint    ##
#############################################
#############################################

import json

import jsonpickle
from flask import session, jsonify

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.gui.breadcrumbs import Breadcrumbs

@auth_required
def setchks_session():
    
    setchks_session=gui_setchks_session.get_setchk_session(session)

    # surely there has to be a simplification to the line below!
    return jsonify(json.loads(jsonpickle.encode(setchks_session, unpicklable=False)))

