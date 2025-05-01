import os, json, jsonpickle

import logging
logger=logging.getLogger()

from flask import jsonify

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow

def do_check(setchks_session=None, setchk_results=None):

    """
    NB This does not handle the SRIL case yet. Spec needs updating and then can be included

    """


    selected_sct_version = setchks_session.sct_version.date_string
    latest_sct_version   = setchks_session.available_sct_versions[0].date_string
    
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # this is just blank or header rows
    
    n_CID_ISR=0
    n_CID_NISR_CID_ILR=0
    n_CID_NISR_CID_NILR=0
    n_CID_NISR_SRIL=0
    n_DID_ISR=0
    n_DID_NISR_DID_ILR=0
    n_DID_NISR_DID_NILR=0
    n_DID_NISR_SRIL=0
    
    #The cases to handle are
    # "CID_NISR_CID_NILR" (01)
    # "CID_NISR_SRIL" (09 NEW)
    # "CID_NISR_CID_ILR" (02)
    # "DID_NISR_DID_NILR" (04)
    # "DID_NISR_SRIL" (10 NEW)
    # "DID_NISR_DID_ILR_CID_ISR" (05)
    # "DID_NISR_DID_ILR_CID_NISR" (05)
    # OK = (03)
    # INVALID_SCTID = (07)
    # BLANK_ENTRY = (08)

    at_least_one_valid_SCTID=False

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            if mr.C_Id_why_none not in ["BLANK_ENTRY", "INVALID_SCTID"]:
                at_least_one_valid_SCTID=True # this is used for seeing whether to nuance the GREEN set level message
            if mr.C_Id_why_none in ["CID_NISR_CID_NILR"]: 
                n_CID_NISR_CID_NILR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-01")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Concept Id does not appear, "
                    "as an active or inactive Concept, "
                    f"in the selected release {selected_sct_version}. "
                    f"Neither does it appear in the most recent release {latest_sct_version}."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["CID_NISR_SRIL"]: 
                n_CID_NISR_SRIL+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-09")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Concept Id does not appear, "
                    "as an active or inactive Concept, "
                    "in the selected release."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="CID_NISR_CID_ILR": 
                n_CID_NISR_CID_ILR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-02")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Concept Id does not appear, "
                    "as an active or inactive Concept, "
                    f"in the selected release {selected_sct_version}, "
                    f"but it does appear in the most recent release {latest_sct_version}. "
                    "This suggests the Concept has been introduced after the selected SNOMED release. " 
                    "Consider removing the Concept or selecting a later release."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="ENTERED": 
                n_CID_ISR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-03")
                check_item.outcome_level="DEBUG"
                check_item.general_message="OK"
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_DID_NILR"]: 
                n_DID_NISR_DID_NILR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-04")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Description Id does not appear, "
                    "as an active or inactive Description, "
                    f"in the selected release {selected_sct_version}. "
                    f"Neither does it appear in the most recent release {latest_sct_version}."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_SRIL"]:
                n_DID_NISR_SRIL+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-10")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Description Id does not appear, "
                    "as an active or inactive Description, "
                    "in the selected release."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_DID_ILR_CID_ISR", "DID_NISR_DID_ILR_CID_NISR"]: # CHK02-OUT-05 
                n_DID_NISR_DID_ILR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-05")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The provided Description Id does not appear, "
                    "as an active or inactive Description, "
                    f"in the selected release {selected_sct_version}, "
                    f"but it does appear in the most recent release {latest_sct_version}. "
                    "This suggests the Description has been introduced after the selected SNOMED release. " 
                    "Consider removing the Description or selecting a later release."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="DERIVED": # CHK02-OUT-06
                n_DID_ISR+=1
                #<check_item>
                check_item=CheckItem("CHK02-OUT-06")
                check_item.outcome_level="DEBUG"
                check_item.general_message="OK"
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="INVALID_SCTID": 
                #<check_item>
                check_item=CheckItem("CHK02-OUT-07")
                check_item.outcome_level="DEBUG"
                check_item.general_message=(
                    "The unexpected value in the Identifier column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": 
                #<check_item>
                check_item=CheckItem("CHK02-OUT-08")
                check_item.outcome_level="DEBUG"
                check_item.general_message=(
                    "The blank in the Identifier column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            else:
                #<check_item>
                check_item=CheckItem("CHK02-OUT-NOT_FOR_PRODUCTION")
                check_item.outcome_level="DEBUG"
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                #</check_item>
                this_row_analysis.append(check_item)
        else:
            #<check_item>
            check_item=CheckItem("CHK02-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)
            #</check_item>


    setchk_results.set_analysis["Messages"]=[] 

    n_ISR       = n_CID_ISR + n_DID_ISR
    n_NISR_ILR  = n_CID_NISR_CID_ILR  + n_DID_NISR_DID_ILR
    n_NISR_NILR = n_CID_NISR_CID_NILR + n_DID_NISR_DID_NILR
    n_NISR_SRIL = n_CID_NISR_SRIL     + n_DID_NISR_SRIL
    n_NISR      = n_NISR_ILR + n_NISR_NILR + n_NISR_SRIL

    if n_NISR==0:
        if at_least_one_valid_SCTID:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"[GREEN] This check has detected no issues." 
                        ),
                    outcome_code="CHK02-OUT-18",
                    )
                )
            #</set_level_message>
        else:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                         "[AMBER] This check has detected no issues. However no Identifiers could be checked, as the file contains "
                         "no Identifiers conforming to the SCTID data type." 
                        ),
                    outcome_code="CHK02-OUT-22",
                    )
                )
            #</set_level_message>
    else:
    
        if n_NISR_SRIL!=0:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"[RED] There are Identifiers in this value set that do not appear, "
                         "as active or inactive concepts, in the selected release. " 
                        f"These must be removed or corrected for the full suite of Set Checks to be performed."
                        ),
                    outcome_code="CHK02-OUT-21",
                    )
                )
            #</set_level_message>
        elif n_NISR_ILR!=0:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"[RED] There are Identifiers in this value set that do not appear, "
                         "as active or inactive concepts, in the selected release. " 
                        f"These must be removed or corrected for the full suite of Set Checks to be performed. "
                        f"Some of these Identifiers appear in the latest release which suggests that the value set may "
                        f"correspond to a later release than your selected release."
                        ),
                    outcome_code="CHK02-OUT-19",
                    )
                )
            #</set_level_message>
        else:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"[RED] There are Identifiers in this value set that do not appear, "
                         "as active or inactive concepts, in the selected release. "
                        f"These must be removed or corrected for the full suite of Set Checks to be performed. "
                        f"None of these Identifiers appear in any releases later than your selected release."
                        ),
                    outcome_code="CHK02-OUT-17",
                    )
                )
            #</set_level_message>

        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing Identifiers that DO appear " 
                    f"in the selected release"
                    ),
                value=n_ISR,
                outcome_code="CHK02-OUT-11",
                )
            )
        #</set_level_count>
        
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing Identifiers that DO NOT appear " 
                    f"in the selected release"
                    ),
                value=n_NISR,
                outcome_code="CHK02-OUT-20",
                )
            )
        #</set_level_count>
        
        if n_NISR_ILR!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    descriptor=(
                        f"Number of rows containing Identifiers that DO NOT appear " 
                        f"in the selected release but that DO appear in the latest release"
                        ),
                    value=n_NISR_ILR,
                    outcome_code="CHK02-OUT-12",
                    )
            )
            #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    descriptor=(
                        f"Number of rows containing Identifiers that DO NOT appear " 
                        f"in the selected release and that also DO NOT appear in the latest release"
                        ),
                    value=n_NISR_NILR,
                    outcome_code="CHK02-OUT-13",
                    )
            )
            #</set_level_count>

        