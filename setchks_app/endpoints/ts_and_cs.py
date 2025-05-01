#############################################
#############################################
##     ts_and_cs endpoint                  ##
#############################################
#############################################

import datetime

from flask import session, request, render_template, redirect

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.gui.breadcrumbs import Breadcrumbs

@auth_required
def ts_and_cs():
    if "accept" in request.args.keys():
        session["ts_and_cs_accepted"]=datetime.datetime.now().strftime('%d %b %Y')
        return redirect("/data_upload")
    else:
        setchks_session=gui_setchks_session.get_setchk_session(session)
        if "ts_and_cs_accepted" in session:
            setchks_session.ts_and_cs_accepted=session["ts_and_cs_accepted"]
        bc=Breadcrumbs()
        bc.set_current_page("data_upload")
        return render_template(
            "ts_and_cs.html",
            breadcrumbs_styles=bc.breadcrumbs_styles,
            setchks_session=setchks_session,
            )