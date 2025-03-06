from flask import flash, redirect, url_for, session, request
import os, functools, time
from setchks_app.identity_mgmt.get_token import get_token_from_refresh_token

########################################################
#
# NB these two wrappers are very similar and it should be possible to give the wrapper an argument
# however could not get this to work without Flask throwing (yet more) errors about overwriting endpoints
# so for now need to make sure any necessary changes are made to both wrappers
#
########################################################


def auth_required(f):
    @functools.wraps(f) # not quite sure why added this but now if remove it get overwriting existing endpoint error
    def wrap2(*args, **kwargs):
        authorized=False
        have_token='jwt_token' in session.keys()
        if have_token:
            jwt_token=session['jwt_token']
            print(jwt_token)
            if time.time()<jwt_token['exp']:
                authorized=True
            else:
                session['jwt_token']=get_token_from_refresh_token(refresh_token=jwt_token['refresh_token'])
                authorized ='id_token' in session['jwt_token']
            
        if authorized:
            if "cognito:groups" in jwt_token:
                cognito_group_memberships=jwt_token["cognito:groups"]
            else:
                cognito_group_memberships={}
            level_allowed=True 
            if os.environ['DEPLOYMENT_ENV'] == "AWS":
                if os.environ['ENV'] !="demo": # only let vsmt_internal into environments other than demo
                    level_allowed="vsmt_internal" in cognito_group_memberships
            
            
            ####################################################################
            # put up closed message in DEMO environment for non internal users #
            ####################################################################
            if os.environ['ENV'] == "test":  # change this to demo to close down demo
              if "vsmt_internal" not in cognito_group_memberships:
                return "The Set Checks (Proof of Concept) is no longer available"

            if level_allowed:
                return f(*args, **kwargs)
            else:
                return "You are not authorised to access this endpoint in this environment"    
        
        else:
            session['function_provoking_auth_call']='/data_upload'
            return redirect(url_for('setchks_app.cognito_test'))
    return wrap2

def auth_required_admin(f):
    @functools.wraps(f) # not quite sure why added this but now if remove it get overwriting existing endpoint error
    def wrap2(*args, **kwargs):
        # print(list(session.keys()))
        authorized=False
        have_token='jwt_token' in session.keys()
        if have_token:
            jwt_token=session['jwt_token']
            print(jwt_token)
            # print(jwt_token)
            if time.time()<jwt_token['exp']:
                authorized=True
            else:
                session['jwt_token']=get_token_from_refresh_token(refresh_token=jwt_token['refresh_token'])
                authorized ='id_token' in session['jwt_token']
        if authorized:
            if "cognito:groups" in jwt_token:
                cognito_group_memberships=jwt_token["cognito:groups"]
            else:
                cognito_group_memberships={}
            level_allowed="vsmt_admin" in cognito_group_memberships
            # print(f"cognito_group_memberhips:{cognito_group_memberships}")
            if level_allowed:
                return f(*args, **kwargs)
            else:
                return "You are not authorised to access this endpoint in this environment"    
        else:
            # session['function_provoking_auth_call']=url_for('setchks_app.'+f.__name__) # trying dropping this to simplify things
            # session['function_provoking_auth_call']='/data_upload'
            return redirect(url_for('setchks_app.cognito_test'))
    return wrap2



