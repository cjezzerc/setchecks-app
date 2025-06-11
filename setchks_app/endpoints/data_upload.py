#####################################
#####################################
##     data upload endpoint        ##
#####################################
#####################################

import logging
from flask import request, session, render_template

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.ts_and_cs.wrapper import accept_ts_and_cs_required
from setchks_app.gui.breadcrumbs import Breadcrumbs


# @bp.route('/', methods=['GET'])
# @bp.route('/data_upload', methods=['GET','POST'])
@auth_required
@accept_ts_and_cs_required  # NB this must come AFTER the auth_required for various redirects to work
def data_upload():
    setchks_session = gui_setchks_session.get_setchk_session(session)

    if "load_file_behaviour" in request.form:
        setchks_session.load_file_behaviour = request.form["load_file_behaviour"]

    bc = Breadcrumbs()
    bc.set_current_page("data_upload")

    return render_template(
        "data_upload.html",
        setchks_session=setchks_session,
        breadcrumbs_styles=bc.breadcrumbs_styles,
    )
