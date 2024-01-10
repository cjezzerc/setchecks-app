import json, jsonpickle, zlib

from bson import json_util
import gridfs
from setchks_app.mongodb import get_mongodb_client

def store_setchks_session(
    setchks_session=None,
    ):
    
    mongodb_client=get_mongodb_client.get_mongodb_client()
    db=mongodb_client["mgmt_info_setchks_sessions"]
    fs=gridfs.GridFS(db)
    ssjsgz=zlib.compress(jsonpickle.encode(setchks_session).encode())
    run_id=setchks_session.uuid+":"+setchks_session.time_started_processing
    fs.put(ssjsgz, run_id=run_id)

def get_setchks_session(
        run_id=None,
        ):
    mongodb_client=get_mongodb_client.get_mongodb_client()
    db=mongodb_client["mgmt_info_setchks_sessions"]
    fs=gridfs.GridFS(db)
    # print(f"{{'run_id':'{run_id}'}}")
    query_string=f'{{"run_id":"{run_id}"}}'
    # data=fs.find_one(query_string)
    # data=db["fs.files"].find_one({"run_id":run_id})
    data=fs.find_one({"run_id":run_id}).read()
    # data=fs.get(file_id=file_id)
    # data=fs.list()
    # data=fs.get(file_id="659e8e0c8b24f81082f335f2")
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    print(query_string)
    print(data)
    print("===========================")
    print("===========================")
    print("===========================")
    print("===========================")
    ndata=jsonpickle.decode(zlib.decompress(data).decode())
    return ndata 



