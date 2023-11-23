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

    outcome_codes_matrix={
        "i"   :["01"                                         ],
        "ii"  :[     "02","03","04","05",          "08"      ],
        "iii" :[                         "06"                ],
        "iv"  :[          "03","04","05",                    ],
        "v"   :[          "03","04","05",     "07",          ],
        "vi"  :[          "03","04","05",          "08",     ],
        "vii" :[          "03","04","05",     "07","08",     ],
        "viii":["01",                                   "09",],
        "ix"  :["01",                                        ],
        "vi"  :[     "02","03","04","05",           "08",    ],
    }

    def generate_check_item(
        outcome_code=None,    
        preferred_term=None,
        implied_concept_id=None,
        implied_dterm=None,
        dterm_type=None,
        description_inactive=None,
        corrected_dterm=None,
        data_entry_extract_type=None,
        ):
        if outcome_code=="CHK03-OUT-01":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The preferred term for this concept is -->"
                )
            check_item.row_specific_message=(
                f"{preferred_term}"
                )
        elif outcome_code=="CHK03-OUT-02":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The provided description ID corresponds to the description term -->"
                )
            check_item.row_specific_message=(
                f"{implied_dterm}"
                )
        elif outcome_code=="CHK03-OUT-03":
            if description_inactive==True:
                check_item=CheckItem(outcome_code=outcome_code)
                check_item.general_message=(
                    "This description term is inactive. " 
                    "You should consider selecting an active term " 
                    "for the corresponding concept (See tab TBI)"
                    )
            else:
                check_item=None
        elif outcome_code=="CHK03-OUT-04":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The description term has a term type of -->"
                )
            check_item.row_specific_message=(
                f"{dterm_type}"
                )
        elif outcome_code=="CHK03-OUT-05":
            if dterm_type=="fsn" and data_entry_extract_type in ["ENTRY_PRIMARY","ENTRY_OTHER"]: 
                check_item=CheckItem(outcome_code=outcome_code)
                check_item.general_message=(
                    "The description term type is a Fully Specified Name (FSN) "
                    "which should not be presented for Data Entry purposes. "  
                    "You should choose another term for the corresponding concept (See tab TBI)"
                    )
            else:
                check_item=None
        elif outcome_code=="CHK03-OUT-06":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The term given does not correspond to this concept ID. "
                "Please select either the preferred term or a synonym for this Concept ID. "
                "(See tab TBI)"
                )
        elif outcome_code=="CHK03-OUT-07":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "This term has the correct wording, but does not conform to the capitalisation rule "
                "that has been specified for this particular term. " 
                "In some cases using incorrect capitalisation can lead to significant Clinical Risk."
                "According to its Case Significance Rule this description term should be written as -->"
                )
            check_item.row_specific_message=(
                f"{corrected_dterm}"
                )
        elif outcome_code=="CHK03-OUT-08":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The provided description ID corresponds to this Concept ID -->"
                )
            check_item.row_specific_message=(
                f"{implied_concept_id}"
                )
        elif outcome_code=="CHK03-OUT-08":
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "The provided description term does not correspond to the provided Description ID. "
                "The correct description term for this Description ID is -->"
                )
            check_item.row_specific_message=(
                f"{implied_dterm}"
                )  
        else:
            check_item=CheckItem(outcome_code=outcome_code)
            check_item.general_message=(
                "Unrecognized outcome code"
                )
        
        return check_item
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

                # at this level and deeper can assume have either a C_Id or a D_Id
                if setchks_session.columns_info.have_dterm_column is False: # no DTERM column
                    if mr.C_Id_entered is not None:
                        leaf="i" # Just C_Id given (No DTERM column)
                    else:
                        leaf="ii" # Just D_Id given (No DTERM column)
                else: # Have Term column
                    if mr.D_Term_entered=="": # Term is blank
                        if mr.C_Id_entered is not None:
                            leaf="ix" # C_Id entered, but Term is blank
                        else:
                            leaf="x" # D_Id entered, but Term is blank
                    else: # A Term has been entered
                        if mr.C_Id_entered is not None: # CID and Term
                            if not mr.congruence_of_C_Id_entered_and_D_Term_entered_case_insens:
                                leaf="iii" # Term is not one for this entered C_Id
                            else:
                                if mr.congruence_of_C_Id_entered_and_D_Term_entered_csr:
                                    leaf="iv" # Term is close to being one for this entered_C_Id but does not pass case significance
                                else:
                                    leaf="v" # Term fully matches one for this entered C_Id, including case significance
                        else: # must be DID and Term
                            if mr.congruence_of_D_Id_entered_and_D_Term_entered_case_insens: 
                                if mr.congruence_of_D_Id_entered_and_D_Term_entered_csr:
                                    leaf="vi" # Term is nearly correct for this D_Id, but does not pass case significance
                                else:
                                    leaf="vii" # Term is fully correct for this D_Id, including case significance
                            else:
                                leaf="viii" # Term is incorrect for this DID
                #
                # need to build up the items that need to pass into generate_check_item here
                #
                for outcome_code_digits in outcome_codes_matrix[leaf]:
                    check_item=generate_check_item(outcome_code=f"CHK03-OUT-{outcome_code_digits}")
                    if check_item:
                        this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item=CheckItem("CHK03-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK03-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
    
    # msg=(
    # f"There are {n_CONCEPTS_NOT_RECOMMENDED} concepts "  
    # f"in the value set that are categorised as ‘not recommended’ for the "
    # f"{data_entry_extract_type} data entry type assigned to this value set."
    # )
    # setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)