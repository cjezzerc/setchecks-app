#!/usr/bin/env python

import vsmt_uprot
import sys
print("sys.path is", sys.path)

debug=True
if len(sys.argv)>1:
    debug=sys.argv[1]


# NB if (below) set use_flask_session_and_redis=True then need a redis docker running (see the _init_.py in vsmt_uprot folder)
# BUT if do NOT use flask_session and redis then the trial uplaoad will fail because it cannot store the Vs_check_session to the regular session cookie

# vsmt_uprot.create_app().run(debug=debug, host='0.0.0.0')
vsmt_uprot.create_app(use_flask_session_and_redis=True).run(debug=debug, host='0.0.0.0')

