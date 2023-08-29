"""routine to assist with setchks_session handling in webapp setting"""

import vsmt_uprot.setchks.setchks_session
import vsmt_uprot.terminology_server_module
import os

def get_setchk_session(session=None):
    """grab setchks_session from flask-session(redis) or create a new one)"""

    if 'setchks_session' in session.keys(): # grab setchks_session from session variable if it is in there
        setchks_session=session['setchks_session']
    else: # otherwise initialise the setchks_session object and save to session variable
        setchks_session=vsmt_uprot.setchks.setchks_session.SetchksSession()
        #
        # Need to think of safer mechanism to set terminology server so does not time out
        #
        setchks_session.terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                            auth_url=os.environ["ONTOAUTH_INSTANCE"])
        session['setchks_session']=setchks_session 
    return setchks_session