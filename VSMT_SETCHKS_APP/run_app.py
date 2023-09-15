#!/usr/bin/env python

import setchks_app.create_app
import sys

debug=True
if len(sys.argv)>1:
    debug=sys.argv[1]

setchks_app.create_app.create_app().run(debug=debug, host='0.0.0.0', port=5000)
