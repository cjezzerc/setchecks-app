import time

from flask import session

def is_authorised():
    authorized=False
    have_token='jwt_token' in session.keys()
    if have_token:
        jwt_token=session['jwt_token']
        if 'exp' in jwt_token:
            if time.time()<jwt_token['exp']:
                authorized=True
    return authorized
    