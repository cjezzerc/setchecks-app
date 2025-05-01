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
    data=fs.find_one({"run_id":run_id}).read()
    ndata=jsonpickle.decode(zlib.decompress(data).decode())
    return ndata 



