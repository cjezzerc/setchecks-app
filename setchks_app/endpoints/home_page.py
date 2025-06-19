#######################################
#######################################
##        home page endpoint         ##
#######################################
#######################################

from flask import redirect, url_for


def home_page():
    return redirect(url_for("setchks_app.about"))
