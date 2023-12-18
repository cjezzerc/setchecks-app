import os

import logging
logger=logging.getLogger()

from flask import current_app

import setchks_app.terminology_server_module

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow


def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    ##################################################################
    ##################################################################
    ##################################################################
    # Fetch and process membership of refset from Terminology Server #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    # Fetch membership of default exclusion filter refset
    # ** Assumes this refset will never be large enough to require paging
    default_exclusion_filter_refset_id=999002571000000104
    
    # really should check for when token expires first but that did not seem to be working
    setchks_session.terminology_server=setchks_app.terminology_server_module.TerminologyServer()
    refset_response=setchks_session.terminology_server.do_expand(refset_id=default_exclusion_filter_refset_id, sct_version=setchks_session.sct_version.formal_version_string, add_display_names=True)

    # Convert response into a dictionary of display strings keyed by concept_id
    # and a set of concept_ids
    # ** Really should make the data returned by terminology_server.do_expand be less string based 
    refset_concept_ids=set()
    refset_displays={}
    for response_string in refset_response:
        f=[x.strip() for x in response_string.split("|")]
        concept_id, display, active_indication=f
        refset_concept_ids.add(concept_id)
        refset_displays[concept_id]=display
    
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
    n_OUTCOME_IN_EXCL_REF_SET=0
    n_NO_OUTCOME_EXCL_REF_SET=0



    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                if concept_id in refset_concept_ids:
                    n_OUTCOME_IN_EXCL_REF_SET+=1
                    #<check_item>
                    check_item=CheckItem("CHK06-OUT-01")
                    check_item.outcome_level="ISSUE"
                    check_item.general_message=(
                        "This Concept is not recommended for use within a patient record, "
                        "i.e., is not recommended for clinical data entry. Please remove or replace this Concept."
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
                else: 
                    n_NO_OUTCOME_EXCL_REF_SET+=1
                    #<check_item>
                    check_item=CheckItem("CHK06-OUT-02")
                    check_item.outcome_level="DEBUG"
                    check_item.general_message="OK"
                    #</check_item>
                    this_row_analysis.append(check_item)

            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                #<check_item>
                check_item=CheckItem("CHK06-OUT-NOT_FOR_PRODUCTION")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                #</check_item>
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            #<check_item>
            check_item=CheckItem("CHK06-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            #</check_item>
            this_row_analysis.append(check_item)

    
    
    setchk_results.set_level_table_rows=[] 
    if n_OUTCOME_IN_EXCL_REF_SET==0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    f"[GREEN] This check has detected no issues." 
                    ),
                outcome_code="CHK06-OUT-07",
                )
            )
        #</set_level_message>
    else:   
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[RED] This value set contains Concepts that are found in the "
                    "UK Default Exclusion Filter Reference Set, "
                    "which contains Concepts that have been assessed as being "
                    "not recommended for use within a patient record, "
                    "i.e., not recommended for clinical data entry. "
                    "Such Concepts should be removed or replaced."
                    ),
                outcome_code="CHK06-OUT-06",
                )
            )
        #</set_level_message>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows where the Concept is in the UK Default Exclusion Reference Set"
                    ),
                value=f"{n_OUTCOME_IN_EXCL_REF_SET}",
                outcome_code="CHK06-OUT-05",
                )
            )
        #</set_level_count>
   