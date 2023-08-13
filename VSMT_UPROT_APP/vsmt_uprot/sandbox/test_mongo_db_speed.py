#!/usr/bin/env python

import sys, os, pprint, time

from pymongo import MongoClient

client=MongoClient()
db=client['VSMT_uprot_app']
db_document=db['concepts']

root_id=int(sys.argv[1])

t0=time.time()
root_concept=db_document.find_one({'code':root_id})
t1=time.time()
# root_concept['descendants']=set(root_concept['descendants'])
print(root_id in root_concept['descendants'])
print(type(root_concept['descendants']))

print("%10.6f %s" % ((t1-t0), len(root_concept['descendants'])))
sys.exit()

# for x in root_concept:
    # print(x)

n=0
t0=time.time()
for code in root_concept['descendants']:
    # t0=time.time()
    concept=db_document.find_one({'code':code})
    n+=1
    # t1=time.time()
    # print("%10.6f %20s %s" % (t1-t0, code, concept['display']))
t1=time.time()
print("%10.6f %s" % (t1-t0, n))

# print(len(list(root_concept)))
# pprint.pprint(root_concept)

# t0=time.time()
# a=tc.find({'id':'8801005'})
# t1=time.time()
# print(t1-t0)

# for b in a:
#     print(b)
