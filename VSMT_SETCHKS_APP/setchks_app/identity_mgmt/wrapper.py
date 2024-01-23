from flask import flash, redirect, url_for, session, request
import os, functools, time
from setchks_app.identity_mgmt.get_token import get_token_from_refresh_token

def auth_required(f):
    # @wraps(f)
    @functools.wraps(f) # not quite sure why added this but now if remove it get overwriting existing endpoint error
    def wrap2(*args, **kwargs):
        # print(list(session.keys()))
        authorized=False
        have_token='jwt_token' in session.keys()
        if have_token:
            jwt_token=session['jwt_token']
            # print(jwt_token)
            if time.time()<jwt_token['exp']:
                authorized=True
            else:
                session['jwt_token']=get_token_from_refresh_token(refresh_token=jwt_token['refresh_token'])
                authorized ='id_token' in session['jwt_token']
        if authorized:
            return f(*args, **kwargs)
        else:
            session['function_provoking_auth_call']=url_for('setchks_app.'+f.__name__)
            return redirect(url_for('setchks_app.cognito_test'))
    return wrap2