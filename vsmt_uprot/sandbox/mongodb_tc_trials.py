#!/usr/bin/env python

import os, sys, pprint, json
import time

from pymongo import MongoClient

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/')
from vsmt_uprot.terminology_server_module import TerminologyServer
from vsmt_uprot.vsmt_valueset import VSMT_VersionedValueSet

def add_descendants_to_tc(id=None, tc=None):
    expansion=terminology_server.do_expand(ecl='<'+id)
    entry={}
    entry['id']=id
    entry['descendants']=expansion
    tc.insert_one(entry)
    print("Added %s descendant for id %s" % (len(expansion), id))


terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])

client=MongoClient()
db=client['VSMT_uprot_app']
tc=db['tc']

# id='73211009'
# add_descendants_to_tc(id=id, tc=tc)

# d=tc.find_one({'id':id})['descendants']

# for d_id in d:
#     add_descendants_to_tc(id=str(d_id), tc=tc)

t0=time.time()
a=tc.find({'id':'8801005'})
t1=time.time()
print(t1-t0)

for b in a:
    print(b)
