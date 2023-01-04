#!/usr/bin/env python

import vsmt_uprot_app
import sys
print("sys.path is", sys.path)

debug=True
if len(sys.argv)>1:
    debug=sys.argv[1]

vsmt_uprot_app.create_app().run(debug=debug, host='0.0.0.0')
