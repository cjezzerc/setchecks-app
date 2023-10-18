#!/usr/bin/env python

import sys

import setchks_app.create_app
from setchks_app.redis.rq import start_rq_worker_if_none_running

start_rq_worker_if_none_running()

debug=True
if len(sys.argv)>1 and sys.argv[1]=="false":
    debug=False

setchks_app.create_app.create_app().run(debug=debug, host='0.0.0.0', port=5000)
