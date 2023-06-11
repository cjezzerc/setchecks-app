#!/usr/bin/env python

import os, sys, pprint, json
import time

from pymongo import MongoClient


def add_descendants_to_tc(id=None, tc=None, concepts=None):
    # expansion=terminology_server.do_expand(ecl='<'+id)
    expansion=list(concepts[id].descendants)
    entry={}
    entry['id']=id
    entry['descendants']=expansion
    tc.insert_one(entry)
    print("Added %s descendant for id %s" % (len(expansion), id))

##############################
# Load SNOMED-CT from pickle #
##############################
sys.path.append('/cygdrive/c/Users/jeremy/GIT/snomed_python/')
import release_processing
branch_tag="UKCL_v36.0"
concepts=release_processing.read_concepts_pickle_file(branch_tag=branch_tag, verbose=True)

client=MongoClient()
db=client['VSMT_uprot_app']
tc=db['tc']

t0=time.time()

# id=73211009
# id=20957000
id=64572001
add_descendants_to_tc(id=id, tc=tc, concepts=concepts)

d=tc.find_one({'id':id})['descendants']

n_done=1
for d_id in d:
    n_done+=1
    add_descendants_to_tc(id=d_id, tc=tc, concepts=concepts)

t1=time.time()
print(n_done, t1-t0)

# t0=time.time()
# a=tc.find({'id':'8801005'})
# t1=time.time()
# print(t1-t0)

# for b in a:
#     print(b)
