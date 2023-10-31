import os, json, jsonpickle

import logging
logger=logging.getLogger()

from flask import jsonify

def do_check(setchks_session=None, setchk_results=None):

    """
    NB This does not handle the SRIL case yet. Spec needs updating and then can be included

    """
    selected_sct_version = setchks_session.sct_version.date_string
    latest_sct_version   = setchks_session.available_sct_versions[0].date_string
    
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # this is just blank or header rows
    
    n_CID_NISR=0
    n_CID_ISR=0
    n_CID_NILR=0
    n_CID_ILR=0
    n_DID_NISR=0
    n_DID_ISR=0
    n_DID_NILR=0
    n_DID_ILR=0

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            n_FILE_PROCESSABLE_ROWS+=1
            if mr.C_Id_why_none=="CID_NISR_CID_NILR": # CHK02-OUT-01 
                n_CID_NISR+=1
                n_CID_NILR+=1
                check_item={}
                check_item["Result_id"]=1
                check_item["Message"]=(
                    "The Concept Id in the MIXED column " 
                    "is not an identifiable concept in either "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"or the most recent SNOMED release {latest_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="CID_NISR_CID_ILR": # CHK02-OUT-02 
                n_CID_NISR+=1
                n_CID_ILR+=1
                check_item={}
                check_item["Result_id"]=2
                check_item["Message"]=(
                    "The Concept Id in the MIXED column" 
                    "is not an identifiable concept in "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"but is an identifiable concept in the most recent SNOMED release {latest_sct_version}.\n"
                    "This suggests the concept has been introduced after "
                    "the selected SNOMED release; consider removing the concept or selecting a later SNOMED release."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="ENTERED": # CHK02-OUT-03
                n_CID_ISR+=1
                check_item={}
                check_item["Result_id"]=0 
                check_item["Message"]="OK"
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="DID_NISR_DID_NILR": # CHK02-OUT-04 
                n_DID_NISR+=1
                n_DID_NILR+=1
                check_item={}
                check_item["Result_id"]=4
                check_item["Message"]=(
                    "The Description Id in the MIXED column " 
                    "is not an identifiable description in either "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"or the most recent SNOMED release {latest_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_DID_ILR_CID_ISR", "DID_NISR_DID_ILR_CID_NISR"]: # CHK02-OUT-05 
                n_DID_NISR+=1
                n_DID_ILR+=1
                check_item={}
                check_item["Result_id"]=5
                check_item["Message"]=(
                    "The Description Id in the MIXED column " 
                    "is not an identifiable concept in "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"but is an identifiable concept in the most recent SNOMED release {latest_sct_version}.\n"
                    "This suggests the description has been introduced after "
                    "the selected SNOMED release; consider removing the description or selecting a later SNOMED release."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="DERIVED": # CHK02-OUT-06
                n_DID_ISR+=1
                check_item={}
                check_item["Result_id"]=0 
                check_item["Message"]="OK"
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="INVALID_SCTID": # CHK02-OUT-07
                n_FILE_NON_PROCESSABLE_ROWS+=1 
                check_item={}
                check_item["Result_id"]=5
                check_item["Message"]=(
                    "The unexpected value in the MIXED column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": # CHK02-OUT-08 
                n_FILE_NON_PROCESSABLE_ROWS+=1
                check_item={}
                check_item["Result_id"]=5
                check_item["Message"]=(
                    "The blank in the MIXED column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                this_row_analysis.append(check_item)
            else:
                check_item={}
                check_item["Result_id"]=-1
                check_item["Message"]=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (C_Id_why_none={mr.C_Id_why_none})"
                    )
                this_row_analysis.append(check_item)
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows
            check_item={}
            check_item["Message"]="Blank line"
            check_item["Result_id"]=-2 # this flags a blank line
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
    
    for counter, c_or_d, sense, release_word, release_date, in [
        [n_CID_NISR, "Concept",     "not ",  "selected", selected_sct_version],
        [n_CID_ISR,  "Concept",     "",      "selected", selected_sct_version],
        [n_CID_NILR, "Concept",     "not ",  "latest",   latest_sct_version  ],
        [n_CID_ILR,  "Concept",     "",      "latest",   latest_sct_version  ],
        [n_DID_NISR, "Description", "not ",  "selected", selected_sct_version],
        [n_DID_ISR,  "Description", "",      "selected", selected_sct_version],
        [n_DID_NILR, "Description", "not ",  "latest",   latest_sct_version  ],
        [n_DID_ILR,  "Description", "",      "latest",   latest_sct_version  ],
        ]:
        msg=(
            f"There are {counter} rows "  
            f"containing {c_or_d} Ids that are {sense}identifiable " 
            f"in the {release_word} SNOMED release {release_date}, " 
            f"in your input file of {n_FILE_TOTAL_ROWS} rows"
            )
        setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)