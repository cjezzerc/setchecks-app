import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService

from ..check_item import CheckItem

ds=DescriptionsService()
        
       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "ENTRY_PRIMARY"
        "ENTRY_OTHER"
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    dual_mode=setchks_session.sct_version_mode=="DUAL_SCT_VERSIONS"
    if not dual_mode:
        sct_version=setchks_session.sct_version # NB this is an sct_version *object*
        concepts=ConceptsDict(sct_version=sct_version.date_string)
    else: # in the DUAL_SCT_VERSIONS case the main sct_version is set to the later on (setchks_session.sct_version_b)
          # and have earlier_sct_version which is set to setchks_session.sct_version
          # the only info needed from the earlier_sct_version is about concept activity
        sct_version=setchks_session.sct_version_b
        earlier_sct_version=setchks_session.sct_version
        concepts=ConceptsDict(sct_version=sct_version.date_string)
        concepts_earlier_sct_version=ConceptsDict(sct_version=earlier_sct_version.date_string)

    ###########################################################################
    # First pass over all rows to build up membership and supp                #
    # tab rows so that can reference things correctly when do second pass     #     
    ###########################################################################
   
    rows_with_this_cid_entered={}
    rows_with_this_did_entered={}

    n_DUPLICATE_CIDS=0
    n_DUPLICATE_DIDS=0

    for i_data_row, mr in enumerate(setchks_session.marshalled_rows):
        cid_for_concept_referred_to=mr.C_Id
        cid_entered=mr.C_Id_entered
        did_entered=mr.D_Id_entered
        if cid_for_concept_referred_to is not None:
            if cid_entered:
                if cid_entered not in rows_with_this_cid_entered:
                    rows_with_this_cid_entered[cid_entered]=set()
                rows_with_this_cid_entered[cid_entered].add(i_data_row)
            if did_entered:
                if did_entered not in rows_with_this_did_entered:
                    rows_with_this_did_entered[did_entered]=set()
                rows_with_this_did_entered[did_entered].add(i_data_row)

    duplicated_cid_rows={}
    for cid_entered, rows in rows_with_this_cid_entered.items():
        if len(rows)>1:
            n_DUPLICATE_CIDS+=1
            for row in rows:
                assert row not in duplicated_cid_rows
                # duplicated_cid_rows[row]=rows.difference(set([row])) # set operation leaves all rows except this one
                duplicated_cid_rows[row]=rows
  
    duplicated_did_rows={}
    for did_entered, rows in rows_with_this_did_entered.items():
        if len(rows)>1:
            n_DUPLICATE_DIDS+=1
            for row in rows:
                assert row not in duplicated_did_rows
                # duplicated_did_rows[row]=rows.difference(set([row])) # set operation leaves all rows except this one
                duplicated_did_rows[row]=rows

    # # cids_entered=set(rows_with_this_cid_entered.keys())
    # dids_entered=set(rows_with_this_did_entered.keys())
    # cid_entered_with_other_description_id_rows={}
    # for cid_entered, rows in rows_with_this_cid_entered.items():
    #     C_Id_data=ds.get_data_about_concept_id(
    #             concept_id=cid_entered, 
    #             sct_version=setchks_session.sct_version,
    #             )
    #     valid_dids_for_this_cid_entered=set(x["desc_id"] for x in C_Id_data)
    #     dids_in_file_for_this_cid_entered=(
    #         dids_entered.intersection(valid_dids_for_this_cid_entered)
    #         )     
    #     if dids_in_file_for_this_cid_entered != set():
    #         for did in dids_in_file_for_this_cid_entered:
    #             if cid_entered not in cid_entered_with_other_description_id_rows:
    #                 cid_entered_with_other_description_id_rows[cid_entered]=set()
    #             cid_entered_with_other_description_id_rows[cid_entered].update(rows_with_this_did_entered[did])

    ##################################################################
    ##################################################################
    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################
    ##################################################################
    ##################################################################
    
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # with gatekeeper this is just blank or header rows
    

    n_DID_FOR_INCLUDED_CID=0
    n_CID_FOR_INCLUDED_DID=0
    n_DIDS_WITH_OTHER_DID_TO_SAME_CONCEPT=0

    for i_data_row,mr in enumerate(setchks_session.marshalled_rows):
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                cid_entered=mr.C_Id_entered
                did_entered=mr.D_Id_entered
                n_FILE_PROCESSABLE_ROWS+=1
                if cid_entered and i_data_row in duplicated_cid_rows: 
                    check_item=CheckItem("CHK22-OUT-02")
                    check_item.general_message=(
                        "This concept id is duplicated in this file, on row(s)-->"
                        )
                    check_item.row_specific_message=(
                        ", ".join(f"Row {x+1+setchks_session.first_data_row}" 
                                    for x in duplicated_cid_rows[i_data_row])
                        )
                    this_row_analysis.append(check_item)
                # elif cid_entered and cid_entered in cid_entered_with_other_description_id_rows:
                #     check_item=CheckItem("CHK22-OUT-03")
                #     check_item.general_message=(
                #         "This Concept Id refers to the same concept as "
                #         "the Description Ids, on row(s)-->"
                #         )
                #     check_item.row_specific_message=(
                #         ", ".join(f"Row {x+1+setchks_session.first_data_row}" 
                #                     for x in cid_entered_with_other_description_id_rows[cid_entered])
                #         )
                #     this_row_analysis.append(check_item)
                elif did_entered and i_data_row in duplicated_did_rows: 
                    check_item=CheckItem("CHK22-OUT-05")
                    check_item.general_message=(
                        "This description id is duplicated in this file, on row(s)-->"
                        )
                    check_item.row_specific_message=(
                        ", ".join(f"Row {x+1+setchks_session.first_data_row}" 
                                    for x in duplicated_did_rows[i_data_row])
                        )
                    this_row_analysis.append(check_item)
                else:
                    check_item={}
                    check_item=CheckItem("CHK22-01")
                    check_item.outcome_level="INFO"
                    check_item.general_message=(
                    "No duplication issue found"
                    )
                    this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK22-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK22-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
            
    msg=(
    f"There are {n_DUPLICATE_CIDS} duplicated CIDs in the value set" 
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
    f"There are {n_DUPLICATE_DIDS} duplicated DIDs in the value set "  
    )
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)