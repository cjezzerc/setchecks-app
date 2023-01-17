#!/usr/bin/env python

import vsmt_uprot
import sys
print("sys.path is", sys.path)

debug=True
if len(sys.argv)>1:
    debug=sys.argv[1]

vsmt_uprot.create_app().run(debug=debug, host='0.0.0.0')
