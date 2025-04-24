import functools, time, os
from flask import session, redirect, url_for, current_app

def auth_required(f):
    print("In auth required1")
    @functools.wraps(f) 
    def wrap(*args, **kwargs):
        oauth=current_app.config["oauth"]
        authorized=False
        if 'jwt_token' in session:
            print(session['jwt_token'])
            # test if should try to refresh
            print(f"Expiry time(1): {session['jwt_token']['expires_at']}")
            if (time.time()+86400-15)>session['jwt_token']['expires_at']:
                new_token = oauth.auth0.fetch_access_token( 
                    refresh_token=session['jwt_token']['refresh_token'],
                    grant_type='refresh_token',
                    )
                for k,v in new_token.items(): # update the things in new token 
                                              # (so keeps old e.g. "user_info","refresh token" entry)
                    session['jwt_token'][k]=v
                session.modified=True # need this because otherwise Flask does not detect the modification
                                      # because changing a mutable value (dict) in the session dict
                print (f"Refreshing..")
                print(f"New Expiry Time: {session['jwt_token']['expires_at']}")
            if (time.time()+86400-30)<session['jwt_token']['expires_at']:
                authorized=True
            print(f"Authorized: {authorized}")
        if authorized:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('setchks_app.login'))
    return wrap

def admin_users_only(f):
    @functools.wraps(f) 
    def wrap(*args, **kwargs):
        if session['jwt_token']['userinfo']['email'] in eval(os.environ["ADMIN_USERS"]):
            return f(*args, **kwargs)
        else:
            return "You are not authorized to access this endpoint"
    return wrap