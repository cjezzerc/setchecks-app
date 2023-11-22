#!/usr/bin/env python
import sys, os, json

import boto3

sys.path.append('../..')

from setchks_app.descriptions_service.descriptions_service import DescriptionsService

print("About to see if need to get secrets")
if 'ONTOSERVER_USERNAME' not in os.environ:
    print("getting secrets")
    sm_client = boto3.client('secretsmanager', region_name='eu-west-2')
    pw_response = sm_client.get_secret_value(SecretId='vsmt-ontoserver-access')
    passwords = pw_response['SecretString']
    dictionary_pw = json.loads(passwords)
    os.environ['ONTOSERVER_USERNAME']=dictionary_pw['ONTOSERVER_USERNAME']
    os.environ['ONTOSERVER_SECRET']=dictionary_pw['ONTOSERVER_SECRET']
    os.environ['TRUDAPIKEY']=dictionary_pw['TRUDAPIKEY']
    os.environ['DOCUMENTDB_USERNAME']=dictionary_pw['DOCUMENTDB_USERNAME']
    os.environ['DOCUMENTDB_PASSWORD']=dictionary_pw['DOCUMENTDB_PASSWORD']
    print("got secrets")
else:
    print("no need to get secrets")

ds=DescriptionsService()

action=sys.argv[1]

if action=="check_coverage":
    for k,v in ds.check_whether_releases_on_ontoserver_have_collections().items():
        print(f'{k}: {v}')

if action=="make_missing":
    ds.make_missing_collections()

if action=="delete_database": # dangerous! do with intention!
    ds.delete_database()

