import json

from bson import json_util

from setchks_app.mongodb import get_mongodb_client

def store_summary_dict_to_db(
    setchks_session=None,
    ):
    
    concepts_set=set()
    for mr in setchks_session.marshalled_rows:
        if mr.C_Id is not None:
            concepts_set.add(mr.C_Id)

    setchk_set_level_message_codes=[]
    # for setchk_code in setchks_session.setchks_results:
    for setchk_code in [x.setchk_code for x in setchks_session.selected_setchks]:
        if (setchk_code in setchks_session.setchks_run_status  # test needed in case fail gatekeeper
            and 
            setchks_session.setchks_run_status[setchk_code]!="failed"
        ):
            for set_level_table_row in setchks_session.setchks_results[setchk_code].set_level_table_rows:
                if set_level_table_row.simple_message is not None:
                    message_code=set_level_table_row.outcome_code
                    severity=set_level_table_row.simple_message.split()[0][1:-1]
                    if severity !="GREEN":
                        setchk_set_level_message_codes.append(message_code)
        else:
            message_code=setchk_code.split("_")[0]+"-OUT-FAIL"
            setchk_set_level_message_codes.append(message_code)

    summary_dict={}
    summary_dict["Time and date checks were run"]=setchks_session.time_started_processing
    summary_dict["Session uuid"]=setchks_session.uuid
    summary_dict["User email"]=setchks_session.email
    summary_dict["Run identifier"]=setchks_session.uuid+":"+summary_dict["Time and date checks were run"]
    summary_dict["Name of input file"]=setchks_session.filename
    summary_dict["Name of value set"]=setchks_session.vs_name
    summary_dict["Name of report file"]=setchks_session.excel_filename.split("/")[-1]
    summary_dict["Number of rows in file"]=setchks_session.first_data_row+len(setchks_session.marshalled_rows)
    summary_dict["Number of identifiable concepts"]=len(concepts_set)
    summary_dict["Data entry or extract type"]=setchks_session.data_entry_extract_type
    summary_dict["SCT release mode"]=setchks_session.sct_version_mode
    summary_dict["Selected release"]=setchks_session.sct_version.date_string
    summary_dict["Selected release b"]=setchks_session.sct_version_b.date_string
    summary_dict["Verbosity of Excel"]=setchks_session.output_full_or_compact
    summary_dict["Set level messages"]=setchk_set_level_message_codes

    mongodb_client=get_mongodb_client.get_mongodb_client()
    collection=mongodb_client["mgmt_info"]["summaries"]
    collection.insert_one(summary_dict)

def get_summary_info():
    mongodb_client=get_mongodb_client.get_mongodb_client()
    collection=mongodb_client["mgmt_info"]["summaries"]
    data=list(collection.find())

    return json.loads(json_util.dumps(data))



