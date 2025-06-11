import functools
from flask import flash, redirect, url_for, session, request


def accept_ts_and_cs_required(f):
    @functools.wraps(f)
    def wrap_ts_and_cs(*args, **kwargs):
        print(list(session.keys()))
        if "ts_and_cs_accepted" in session.keys():
            return f(*args, **kwargs)
        else:
            return redirect(url_for("setchks_app.ts_and_cs"))

    return wrap_ts_and_cs
