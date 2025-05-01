import os, re, time, datetime, logging
from urllib.parse import quote_plus, urlencode

from flask import session, current_app, redirect, url_for

######################################
######################################
## auth0 login                      ##
######################################
######################################

# @bp.route("/login")
def login():
    return current_app.config["oauth"].auth0.authorize_redirect(
        redirect_uri=url_for("setchks_app.callback", _external=True)
    )


######################################
######################################
## auth0 callback                   ##
######################################
######################################

# @bp.route("/callback", methods=["GET", "POST"])
def callback():
    print("In callback")
    token = current_app.config["oauth"].auth0.authorize_access_token()
    session["jwt_token"] = token
    print(token)
    return redirect("/")

######################################
######################################
## auth0 login                      ##
######################################
######################################

# @bp.route("/logout")
def logout():
    del session['jwt_token']
    return redirect(
        "https://" + os.environ["AUTH0_DOMAIN"]
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("setchks_app.ts_and_cs", _external=True), 
                "client_id": os.environ["AUTH0_CLIENT_ID"],
            },
            quote_via=quote_plus,
        )
    )