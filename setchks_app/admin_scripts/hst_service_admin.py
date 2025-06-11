#!/usr/bin/env python
import sys, os, json

import boto3

sys.path.append("../..")

from setchks_app.descriptions_service.descriptions_service import DescriptionsService

print("About to see if need to get secrets")
if "ONTOSERVER_USERNAME" not in os.environ:
    print("getting secrets")
    sm_client = boto3.client("secretsmanager", region_name="eu-west-2")
    pw_response = sm_client.get_secret_value(SecretId="vsmt-ontoserver-access")
    passwords = pw_response["SecretString"]
    dictionary_pw = json.loads(passwords)
    os.environ["ONTOSERVER_USERNAME"] = dictionary_pw["ONTOSERVER_USERNAME"]
    os.environ["ONTOSERVER_SECRET"] = dictionary_pw["ONTOSERVER_SECRET"]
    os.environ["TRUDAPIKEY"] = dictionary_pw["TRUDAPIKEY"]
    os.environ["DOCUMENTDB_USERNAME"] = dictionary_pw["DOCUMENTDB_USERNAME"]
    os.environ["DOCUMENTDB_PASSWORD"] = dictionary_pw["DOCUMENTDB_PASSWORD"]
    print("got secrets")
else:
    print("no need to get secrets")

hst = DescriptionsService(data_type="hst")

action = sys.argv[1]

if action == "check_coverage":
    for k, v in hst.check_whether_releases_on_ontoserver_have_collections().items():
        print(f"{k}: {v}")

if action == "make_missing":
    hst.make_missing_collections()

if action == "delete_whole_database":  # dangerous! do with intention!
    hst.delete_database()

if action == "delete_one_collection":
    date_string = sys.argv[2]
    hst.delete_one_collection(sct_version=date_string)

if action == "make_one_collection":
    date_string = sys.argv[2]
    hst.pull_release_from_trud(date_string=date_string)

if action == "list_collections":
    for collection_name in hst.get_collection_names():
        print(collection_name)

if action == "show_one_collection_size":
    date_string = sys.argv[2]
    print(hst.get_collection_size(sct_version=date_string))

if action == "show_all_collection_sizes":
    for collection_name in hst.get_collection_names():
        # print(collection_name)
        date_string = collection_name[-8:]
        print(date_string, hst.get_collection_size(sct_version=date_string))
