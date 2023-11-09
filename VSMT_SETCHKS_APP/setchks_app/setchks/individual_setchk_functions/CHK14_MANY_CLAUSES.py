import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService

from ..check_item import CheckItem


       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it can be called for all data_entry_extract_types
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    ##################################################################
    ##################################################################
    ##################################################################
    # Refactor value set                                             #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    value_set_members=set()
    
    for mr in setchks_session.marshalled_rows:
        concept_id=mr.C_Id
        if concept_id is not None:
            value_set_members.add(concept_id)
            
    original_valset, refactored_valset=refactor_core_code.refactor_core_code(
                valset_extens_defn=value_set_members,
                concepts=concepts,
                ) 

    print(refactored_valset)
    setchks_session.refactored_form=refactored_valset
    return
    sys.exit()
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
    
    n_CONCEPTS_ACTIVE=0
    n_CONCEPTS_INACTIVE=0
    n_CONCEPTS_NO_REPLACEMENT=0
    n_CONCEPTS_WITH_REPLACEMENTS=0


    for i_data_row,mr in enumerate(setchks_session.marshalled_rows):
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                if setchk_results.supp_tab_blocks[i_data_row] is None: #"CHK04-OUT-i"
                    n_CONCEPTS_ACTIVE+=1
                    check_item=CheckItem("CHK04-OUT-i")
                    check_item.outcome_level="INFO"
                    check_item.general_message=(
                        "Concept is active"
                        )
                    this_row_analysis.append(check_item)
                elif setchk_results.supp_tab_blocks[i_data_row]==[]: #"CHK04-OUT-ii"
                    n_CONCEPTS_INACTIVE+=1
                    n_CONCEPTS_NO_REPLACEMENT+=1
                    check_item=CheckItem("CHK04-OUT-ii")
                    check_item.general_message=(
                        "This concept is inactive and should be removed. "
                        "There is no suggested replacement for this concept."
                        )
                    this_row_analysis.append(check_item)
                else: #"CHK04-OUT-v"
                    n_CONCEPTS_INACTIVE+=1
                    n_CONCEPTS_WITH_REPLACEMENTS+=1
                    check_item=CheckItem("CHK04-OUT-v")
                    check_item.general_message=(
                        "This concept is inactive and should be removed. "
                        "There is at least one suggested replacement for this concept. "
                        "See supplementary tab for details"
                        )
                    this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK04-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK04-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_mesage="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
            
    msg=(
    f"There are {n_CONCEPTS_ACTIVE} active concepts in the value set" 
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
    f"There are {n_CONCEPTS_INACTIVE} inactive concepts in the value set "  
    )
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
    f"{n_CONCEPTS_NO_REPLACEMENT} inactive concepts in the value set have no replacement"  
    )
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
    f"{n_CONCEPTS_WITH_REPLACEMENTS} inactive concepts in the value set have at least one replacement"  
    )
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)