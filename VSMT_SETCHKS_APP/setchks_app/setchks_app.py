from flask import Blueprint

from setchks_app.endpoints.data_upload import data_upload
from setchks_app.endpoints.column_identities import column_identities
from setchks_app.endpoints.enter_metadata import enter_metadata
from setchks_app.endpoints.select_and_run_checks import select_and_run_checks
from setchks_app.endpoints.feedback import feedback
from setchks_app.endpoints.ts_and_cs import ts_and_cs
from setchks_app.endpoints.setchks_session import setchks_session
from setchks_app.endpoints.auth0 import login, logout, callback
from setchks_app.endpoints.healthy import healthy
from setchks_app.endpoints.rq import rq
from setchks_app.endpoints.redis_check import redis_check
from setchks_app.endpoints.mongodb_check import mongodb_check
from setchks_app.endpoints.session_check import session_check
from setchks_app.endpoints.check_coverage import check_coverage
from setchks_app.endpoints.mgmt_info import mgmt_info

bp = Blueprint('setchks_app', __name__)

# main app pages

bp.add_url_rule("/", view_func=data_upload)
bp.add_url_rule("/data_upload", view_func=data_upload, methods=['GET','POST'])
bp.add_url_rule("/column_identities", view_func=column_identities, methods=['GET','POST'])
bp.add_url_rule("/enter_metadata", view_func=enter_metadata, methods=['GET','POST'])
bp.add_url_rule("/select_and_run_checks", view_func=select_and_run_checks, methods=['GET','POST'])
bp.add_url_rule("/feedback", view_func=feedback)
bp.add_url_rule("/ts_and_cs", view_func=ts_and_cs)   

# user utilities #

bp.add_url_rule("/setchks_session", view_func=setchks_session) 

# auth0 endpoints 

bp.add_url_rule("/login", view_func=login)
bp.add_url_rule("/callback", view_func=callback, methods=["GET", "POST"])
bp.add_url_rule("/logout", view_func=logout)

# diagnostic endpoints 

bp.add_url_rule("/healthy", view_func=healthy)
bp.add_url_rule("/mgmt_info", view_func=mgmt_info)
bp.add_url_rule("/check_coverage", view_func=check_coverage)
bp.add_url_rule("/redis_check", view_func=redis_check)
bp.add_url_rule("/mongodb_check", view_func=mongodb_check)
bp.add_url_rule("/rq", view_func=rq)
bp.add_url_rule("/session_check", view_func=session_check)