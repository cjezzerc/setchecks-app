#############################################
#############################################
##     feedback endpoint                  ##
#############################################
#############################################

from flask import session, render_template

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.gui.breadcrumbs import Breadcrumbs


@auth_required
def feedback():
    setchks_session = gui_setchks_session.get_setchk_session(session)
    bc = Breadcrumbs()
    bc.set_current_page("data_upload")
    return render_template(
        "feedback.html",
        breadcrumbs_styles=bc.breadcrumbs_styles,
        setchks_session=setchks_session,
    )
