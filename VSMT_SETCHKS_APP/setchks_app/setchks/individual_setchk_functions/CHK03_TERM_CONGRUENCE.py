import os, copy

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict



from ..check_item import CheckItem

def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "ENTRY_PRIMARY"
        "ENTRY_OTHER"
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    
    valset_members=set()
    for mr in setchks_session.marshalled_rows:
        if mr.C_Id is not None:
            valset_members.add(mr.C_Id)  
    print(f"valset_members {valset_members}")
   

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
    
    n_CONCEPTS_ACCEPTABLE=0

    data_entry_extract_type=setchks_session.data_entry_extract_type
    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                if True:
                    n_CONCEPTS_ACCEPTABLE+=1
                    check_item=CheckItem("CHK05-OUT-01")
                    check_item.outcome_level="INFO"
                    check_item.general_message=(
                        "OK"
                        )
                    this_row_analysis.append(check_item)
                else:
                    check_item={}
                    check_item=CheckItem("CHK05-OUT-NOT_FOR_PRODUCTION")
                    check_item.general_message=(
                        "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                        f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (unrecognised acceptabiliy)"
                        )
                    this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK06-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK06-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
    
    msg=(
    f"There are {n_CONCEPTS_NOT_RECOMMENDED} concepts "  
    f"in the value set that are categorised as ‘not recommended’ for the "
    f"{data_entry_extract_type} data entry type assigned to this value set."
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)