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

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            if mr.C_Id_why_none in ["CID_NISR_CID_NILR"]: 
                n_CID_NISR_CID_NILR+=1
                check_item=CheckItem("CHK02-OUT-01")
                check_item.general_message=(
                    "The Concept Id in the MIXED column " 
                    "is not an identifiable concept in either "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"or the most recent SNOMED release {latest_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["CID_NISR_SRIL"]: 
                n_CID_NISR_SRIL+=1
                check_item=CheckItem("CHK02-OUT-09")
                check_item.general_message=(
                    "The Concept Id in the MIXED column " 
                    "is not an identifiable concept in the "
                    f"selected SNOMED CT release {selected_sct_version} "
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="CID_NISR_CID_ILR": 
                n_CID_NISR_CID_ILR+=1
                check_item=CheckItem("CHK02-OUT-02")
                check_item.general_message=(
                    "The Concept Id in the MIXED column" 
                    "is not an identifiable concept in "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"but is an identifiable concept in the most recent SNOMED release {latest_sct_version}."
                    "\nThis suggests the concept has been introduced after "
                    "the selected SNOMED release; consider removing the concept or selecting a later SNOMED release."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="ENTERED": 
                n_CID_ISR+=1
                check_item=CheckItem("CHK02-OUT-03")
                check_item.outcome_level="INFO"
                check_item.general_message="OK"
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_DID_NILR"]: 
                n_DID_NISR_DID_NILR+=1
                check_item=CheckItem("CHK02-OUT-04")
                check_item.general_message=(
                    "The Description Id in the MIXED column " 
                    "is not an identifiable description in either "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"or the most recent SNOMED release {latest_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_SRIL"]:
                n_DID_NISR_SRIL+=1
                check_item=CheckItem("CHK02-OUT-10")
                check_item.general_message=(
                    "The Description Id in the MIXED column " 
                    "is not an identifiable description in "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none in ["DID_NISR_DID_ILR_CID_ISR", "DID_NISR_DID_ILR_CID_NISR"]: # CHK02-OUT-05 
                n_DID_NISR_DID_ILR+=1
                check_item=CheckItem("CHK02-OUT-05")
                check_item.general_message=(
                    "The Description Id in the MIXED column " 
                    "is not an identifiable concept in "
                    f"the selected SNOMED CT release {selected_sct_version} "
                    f"but is an identifiable concept in the most recent SNOMED release {latest_sct_version}."
                    "\nThis suggests the description has been introduced after "
                    "the selected SNOMED release; consider removing the description or selecting a later SNOMED release."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id is not None and mr.C_Id_source=="DERIVED": # CHK02-OUT-06
                n_DID_ISR+=1
                check_item=CheckItem("CHK02-OUT-06")
                check_item.outcome_level="DEBUG"
                check_item.general_message="OK"
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="INVALID_SCTID": # CHK02-OUT-07
                check_item=CheckItem("CHK02-OUT-06")
                check_item.outcome_level="FACT"
                check_item.general_message=(
                    "The unexpected value in the MIXED column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": # CHK02-OUT-08 
                check_item=CheckItem("CHK02-OUT-08")
                check_item.general_message=(
                    "The blank in the MIXED column " 
                    "has not been checked against " 
                    f"the selected SNOMED CT release {selected_sct_version}."
                    )
                this_row_analysis.append(check_item)
            else:
                check_item=CheckItem("CHK02-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (C_Id_why_none={mr.C_Id_why_none})"
                    )
                this_row_analysis.append(check_item)
        else:
            check_item=CheckItem("CHK01-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)


    setchk_results.set_analysis["Messages"]=[] 

    n_ISR       = n_CID_ISR + n_DID_ISR
    n_NISR_ILR  = n_CID_NISR_CID_ILR  + n_DID_NISR_DID_ILR
    n_NISR_NILR = n_CID_NISR_CID_NILR + n_DID_NISR_DID_NILR
    n_NISR_SRIL = n_CID_NISR_SRIL     + n_DID_NISR_SRIL
    n_NISR      = n_NISR_ILR + n_NISR_NILR + n_NISR_SRIL

    if n_NISR==0:
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    f"[GREEN] All the identifiers were found in the selected release " 
                    ),
                )
            )
    else:
    
        if n_NISR_SRIL!=0:
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"[RED] There are Identifiers in this value set that do not appear in the selected release. " 
                        f"These must be removed or corrected for the full set of Set Checks to be performed."
                        ),
                    )
                )
        elif n_NISR_ILR!=0:
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"There are Identifiers in this value set that do not appear in the selected release. " 
                        f"These must be removed or corrected for the full set of Set Checks to be performed. "
                        f"Some of these Identifiers appear in the latest release which suggests that the value set may "
                        f"correspond to a later release than the one that you have selected."
                        ),
                    )
                )
        else:
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        f"There are Identifiers in this value set that do not appear in the selected release. " 
                        f"These must be removed or corrected for the full set of Set Checks to be performed. "
                        f"None of these Identifiers appear in any releases of SNOMED later than the one that you have selected"
                        ),
                    )
                )

        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing containing Identifiers that appear " 
                    f"in the selected release"
                    ),
                value=n_ISR,
                )
            )
        
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing containing Identifiers that DO NOT appear " 
                    f"in the selected release"
                    ),
                value=n_NISR,
                )
            )
        
        if n_NISR_ILR!=0:
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    descriptor=(
                        f"Number of rows containing Identifiers that DO NOT appear " 
                        f"in the selected release but that DO appear in the latest release"
                        ),
                    value=n_NISR_ILR,
                    )
            )
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    descriptor=(
                        f"Number of rows containing Identifiers that DO NOT appear " 
                        f"in the selected release and that also DO NOT appear in the latest release"
                        ),
                    value=n_NISR_NILR,
                    )
            )

        