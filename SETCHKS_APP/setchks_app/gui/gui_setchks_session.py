"""routine to assist with setchks_session handling in webapp setting"""

import vsmt_uprot.setchks.setchks_session

def get_setchk_session(session=None):
    """grab setchks_session from flask-session(redis) or create a new one)"""

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        session['setchks_session']=setchks_session 
    return setchks_session