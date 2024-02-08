import json, datetime, os
import openpyxl
from bson import json_util
from setchks_app.mongodb import get_mongodb_client

def get_excel_summaries():
    mongodb_client=get_mongodb_client.get_mongodb_client()
    collection=mongodb_client["mgmt_info"]["summaries"]
    data=list(collection.find())
    for summary in data:
        do=datetime.datetime.strptime(summary['Time and date checks were run'],"%d_%b_%Y__%H_%M_%S")
        summary['timestamp']=do.strftime("%Y%m%d:%H%M%S")
    data.sort(key=lambda x: x["timestamp"])
    wb=openpyxl.Workbook()
    ws=wb.worksheets[0]
    header_row=[
        "timestamp",
        "User email",
        "Time and date checks were run",
        "Run identifier",
        "Name of input file",
        "Time and date checks were run",
        "Name of value set",
        "Name of report file",
        "Number of rows in file",
        "Number of identifiable concepts",
        "Data entry or extract type",
        "SCT release mode",
        "selected_release",
        "selected_release_b",
        "Verbosity of Excel",
        "Set level messages",
        ]
    ws.append(header_row)
    for summary in data:
        output_row=[]
        for key in header_row:
            output_row.append(str(summary.get(key, None)))
        ws.append(output_row)
    
    tmp_folder="/tmp/mgmt_info/excel_summaries/"
    os.system("mkdir -p " + tmp_folder)
    excel_summaries_filename=f"excel_mgmt_info_summaries_{datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S')}.xlsx"
    excel_summaries_filename_full_path=tmp_folder + excel_summaries_filename
    wb.save(excel_summaries_filename_full_path)   
    fh=open(excel_summaries_filename_full_path,'rb') 
    return fh, excel_summaries_filename