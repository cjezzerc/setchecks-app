#############################################
#############################################
##     report MI endpoint                  ##
#############################################
#############################################

import json

import jsonpickle
from flask import request, send_file, jsonify

from setchks_app.mgmt_info.handle_excel_file import get_excel_file 
from setchks_app.mgmt_info.handle_setchks_session import get_setchks_session
from setchks_app.mgmt_info.get_excel_summaries import get_excel_summaries 
from setchks_app.mgmt_info.handle_summary_info import get_summary_info 
from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only

@auth_required
@admin_users_only
def mgmt_info():
    object=request.args.get("object", None)
    run_id=request.args.get("run_id", None)
    if object=="setchks_session":
        ss=get_setchks_session(run_id=run_id)
        return jsonify(json.loads(jsonpickle.encode(ss, unpicklable=False)))
    elif object=="excel_file":
        ef, filename=get_excel_file(run_id=run_id)
        return send_file(ef, download_name=filename) 
    elif object=="excel_summaries":
        esf, es_filename=get_excel_summaries()
        return send_file(esf, download_name=es_filename) 
    else:
        return get_summary_info()