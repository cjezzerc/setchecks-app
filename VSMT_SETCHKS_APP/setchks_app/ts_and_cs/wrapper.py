from flask import flash, redirect, url_for, session, request

def accept_ts_and_cs_required(f):
    # @wraps(f)
    def wrap(*args, **kwargs):
        print(list(session.keys()))
        if 'ts_and_cs_accepted' in session.keys():
            return f(*args, **kwargs)
        else:
            return redirect(url_for('setchks_app.ts_and_cs'))
    return wrap