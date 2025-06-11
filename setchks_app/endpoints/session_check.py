#################################
#################################
#   Simple session endpoint     #
#################################
#################################

import os, datetime, logging
from flask import session
from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only

logger = logging.getLogger(__name__)


@auth_required
@admin_users_only
def session_check():
    logger.info("session check called")
    session["time"] = str(datetime.datetime.now().strftime("%d_%b_%Y__%H_%M_%S"))
    session_contents = [f"{k}:{v}" for k, v in session.items()]
    return f"session:<br><br>{'<br><br>'.join(session_contents)}"
