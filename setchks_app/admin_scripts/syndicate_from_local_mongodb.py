#!/usr/bin/python

import sys, urllib.parse, os

import pymongo


def do_transfers(connection_string=None):
    mongoexport = "/cygdrive/c/Program\ Files/MongoDB/Tools/100/bin/mongoexport.exe"
    mongoimport = '/cygdrive/c/Program\ Files/MongoDB/Tools/100/bin/mongoimport.exe --authenticationDatabase="admin"'

    for db_name, collection_name_root in [
        ("hst", "hst_"),
        ("concepts_service", "concepts_"),
        ("descriptions_service", "sct2_Description_MONOSnapshot-en_GB_"),
    ]:
        collection_name = f"{collection_name_root}{datestring}"
        print(f"Transferring {collection_name}")
        command = f"{mongoexport} -d {db_name} -c {collection_name} | {mongoimport} -d {db_name} -c {collection_name} {connection_string}"
        print(command)
        for line in os.popen(command).readlines():
            print(line[:-1])


def do_indexing(mongo_client=None):
    for db_name, collection_name_root, field in [
        ("hst", "hst_", "old_concept_id"),
        ("hst", "hst_", "new_concept_id"),
        ("concepts_service", "concepts_", "code"),
        ("descriptions_service", "sct2_Description_MONOSnapshot-en_GB_", "concept_id"),
        ("descriptions_service", "sct2_Description_MONOSnapshot-en_GB_", "desc_id"),
        ("descriptions_service", "sct2_Description_MONOSnapshot-en_GB_", "term"),
    ]:

        collection_name = f"{collection_name_root}{datestring}"
        collection = mongo_client[db_name][collection_name]
        print(f"Indexing {collection_name} on {field}")
        collection.create_index(field, unique=False)
    print("Finished indexing")


datestring = sys.argv[1]
remote_url = sys.argv[2]
password = sys.argv[3]

encoded_password = urllib.parse.quote(password)
# connection_string=f'mongodb://myUserAdmin:{encoded_password}@217.154.61.147:27017/'
connection_string = (
    # f"mongodb://myUserAdmin:{encoded_password}@app.setchecks.co.uk:27018/?tls=true"
    # f"mongodb://myUserAdmin:{encoded_password}@{remote_url}:27018/?tls=true"
    f"mongodb://myUserAdmin:{encoded_password}@{remote_url}"
)
mongo_client = pymongo.MongoClient(connection_string)

do_transfers(connection_string=connection_string)
do_indexing(mongo_client=mongo_client)
