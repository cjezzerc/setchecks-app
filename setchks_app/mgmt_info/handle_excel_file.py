import json, jsonpickle, zlib

from bson import json_util
import gridfs
from setchks_app.mongodb import get_mongodb_client


def store_excel_file(
    setchks_session=None,
):

    mongodb_client = get_mongodb_client.get_mongodb_client()
    db = mongodb_client["mgmt_info_excel_files"]
    fs = gridfs.GridFS(db)
    run_id = setchks_session.uuid + ":" + setchks_session.time_started_processing
    full_path_filename = setchks_session.excel_filename
    filename = full_path_filename.split("/")[-1]
    fh = open(full_path_filename, "rb")
    fs.put(fh, filename=filename, run_id=run_id)


def get_excel_file(
    run_id=None,
):
    mongodb_client = get_mongodb_client.get_mongodb_client()
    db = mongodb_client["mgmt_info_excel_files"]
    fs = gridfs.GridFS(db)
    fh = fs.find_one({"run_id": run_id})
    # data=.read()
    return fh, fh.filename
