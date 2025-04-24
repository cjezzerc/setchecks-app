"""routine to assist with setchks_session handling in webapp setting"""

import setchks_app.setchks.setchks_session
import os

def get_setchk_session(session=None):
    """grab setchks_session from flask-session(redis) or create a new one)"""

    if 'setchks_session' in session.keys() and session['setchks_session']!=None: # grab setchks_session from session variable if it is in there
                                                                                # the !=None clause allows for setchks_session to be set to None to
                                                                                # do a hard reset
        setchks_session=session['setchks_session']
        # setchks_session.email=session['jwt_token']['email'] # make sure login email stays current in odd cases where e.g.
        setchks_session.email=session['jwt_token']['userinfo']['email'] # make sure login email stays current in odd cases where e.g.
                                                            # developers switch logins
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=setchks_app.setchks.setchks_session.SetchksSession()
        setchks_session.uuid=session.sid
        # setchks_session.email=session['jwt_token']['email']
        setchks_session.email=session['jwt_token']['userinfo']['email']
        session['setchks_session']=setchks_session 
    return setchks_session