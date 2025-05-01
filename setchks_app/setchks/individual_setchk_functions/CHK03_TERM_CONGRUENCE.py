import os, copy

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.excel.termbrowser import termbrowser_hyperlink



from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow

def generate_check_item(
    outcome_code=None,    
    preferred_term=None,
    implied_concept_id=None,
    implied_dterm=None,
    dterm_type=None,
    description_inactive=None,
    csr_correct_dterm=None,
    data_entry_extract_type=None,
    did_term_type=None,
    did_term_words=None,
    ):
    #<check_item>
    if outcome_code=="CHK03-OUT-01":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="FACT"
        check_item.general_message=(
            "The Preferred Term for this Concept, as identified by the Concept Id, is -->"
            )
        check_item.row_specific_message=(
            f"{preferred_term}"
            )
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-02":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="FACT"
        check_item.general_message=(
            "The provided Description Id corresponds to the Term -->"
            )
        check_item.row_specific_message=(
            f"{implied_dterm}"
            )
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-03":
        if description_inactive==True:
            check_item=CheckItem(outcome_code=outcome_code+did_term_type)
            check_item.outcome_level="ISSUE"
            check_item.general_message=(
                f"The provided {did_term_words} is inactive. " 
                f"You should consider selecting an active {did_term_words} " 
                "for the corresponding Concept."
                )
        else:
            check_item=None
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-04":
        check_item=CheckItem(outcome_code=outcome_code+did_term_type)
        check_item.outcome_level="Conditional: FACT/DEBUG" # DEBUG unless n_FSN_FOR_DATA_ENTRY>0
        check_item.general_message=(
            f"The provided {did_term_words} has a Description Type of -->"
            )
        phrase_to_output={
            "fsn": "Fully Specified Name",
            "pt": "Preferred Term",
            "syn": "Acceptable Synonym",
            "inactive_desc": "Inactive Description",
            None: "No type",
            }
        check_item.row_specific_message=(
            f"{phrase_to_output[dterm_type]}"
            )
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-05":
        if dterm_type=="fsn" and data_entry_extract_type in ["ENTRY_PRIMARY","ENTRY_OTHER"]: 
            check_item=CheckItem(outcome_code=outcome_code+did_term_type)
            check_item.outcome_level="ISSUE"
            check_item.general_message=(
                f"The Description Type of the provided {did_term_words} is Fully Specified Name (FSN). "
                "According to your settings, this is a data entry value set. FSNs should not be presented for data entry purposes. "  
                "You should choose another Term for the corresponding Concept."
                )
        else:
            check_item=None
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-06":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "The provided Term given does not correspond to the Concept identified by the provided Concept Id. "
            "Please select a valid Term for this Concept Id."
            )
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-07":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "The provided Term does not conform to the capitalisation rule "
            "for this particular Term. " 
            "According to its capitalisation rule this Term should be written as -->"
            )
        check_item.row_specific_message=(
            f"{csr_correct_dterm}"
            )
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-08":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="FACT"
        check_item.general_message=(
            "The provided Description Id corresponds to the Concept identified by the Concept Id -->"
            )
        check_item.row_specific_message=(
            termbrowser_hyperlink(sctid=implied_concept_id)
            )

    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-09":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "The provided Term does not correspond to the provided Description Id. "
            "The Term for this Description Id is -->"
            )
        check_item.row_specific_message=(
            f"{implied_dterm}"
            ) 
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-10":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "The entry in the Term column is blank. "
            "The Preferred Term for this Concept is -->"
            )
        check_item.row_specific_message=(
            f"{preferred_term}"
            ) 
    #</check_item>
    #<check_item>
    elif outcome_code=="CHK03-OUT-20":
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "The entry in the Term column is blank. "
            "The Term for this Description Id is -->"
            )
        check_item.row_specific_message=(
            f"{implied_dterm}"
            ) 
    #</check_item>    
    else: # this is just a fall through in case of an unaccounted for code
        check_item=CheckItem(outcome_code=outcome_code)
        check_item.outcome_level="ISSUE"
        check_item.general_message=(
            "Unrecognized outcome code"
            )
    
    return check_item

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
        "i"   :["01",                                                  ],
        "ii"  :[     "02","03","04","05",          "08",               ],
        "iii" :[                         "06",                         ],
        "iv"  :[          "03","04","05",                              ],
        "v"   :[          "03","04","05",     "07",                    ],
        "vi"  :[          "03","04","05",          "08",               ],
        "vii" :[          "03","04","05",     "07","08",               ],
        "viii":["01",                              "08","09",          ],
        "ix"  :[                                             "10",     ],
        "x"   :[          "03","04","05",          "08",          "20",],
    }


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
    
    n_INACTIVE_DESCRIPTION=0
    n_FSN_FOR_DATA_ENTRY=0
    n_TERM_CONCEPT_MISMATCH=0
    n_CAPITALISATION_ISSUE=0
    n_TERM_DID_MISMATCH=0
    n_MISSING_TERM=0

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
                            n_MISSING_TERM+=1
                        else:
                            leaf="x" # D_Id entered, but Term is blank
                            n_MISSING_TERM+=1
                    else: # A Term has been entered
                        if mr.C_Id_entered is not None: # CID and Term
                            if not mr.congruence_of_C_Id_entered_and_D_Term_entered_case_insens:
                                leaf="iii" # Term is not one for this entered C_Id
                            else:
                                if mr.congruence_of_C_Id_entered_and_D_Term_entered_csr:
                                    leaf="iv" # Term fully matches one for this entered C_Id, including case significance
                                else:
                                    leaf="v" # Term is close to being one for this entered_C_Id but does not pass case significance
                        else: # must be DID and Term
                            if mr.congruence_of_D_Id_entered_and_D_Term_entered_case_insens: 
                                if mr.congruence_of_D_Id_entered_and_D_Term_entered_csr:
                                    leaf="vi" # Term is fully correct for this D_Id, including case significance
                                else:
                                    leaf="vii" # Term is nearly correct for this D_Id, but does not pass case significance
                            else:
                                leaf="viii" # Term is incorrect for this DID
         
                #
                # prepare all the items needed in the call to generate_check_item
                # even if the particular outcome_codes do not require them
                # (easier than having requirements per outcome code)
                #
                if mr.D_Term_Type_derived_from_D_Id_entered is not None:
                    dterm_type=mr.D_Term_Type_derived_from_D_Id_entered
                elif mr.D_Term_Type_derived_from_C_Id_entered_and_D_Term_entered:
                    dterm_type=mr.D_Term_Type_derived_from_C_Id_entered_and_D_Term_entered
                else:
                    dterm_type=""
                    #dterm_type="pt" # or we report "pt" as we will be giving pt in a separate message
                if mr.D_Term_derived_from_D_Id_entered is not None:
                    csr_correct_dterm=mr.D_Term_derived_from_D_Id_entered 
                elif mr.D_Term_csr_correct_derived_from_C_Id_entered_and_D_Term_entered:
                    csr_correct_dterm=mr.D_Term_csr_correct_derived_from_C_Id_entered_and_D_Term_entered
                else:
                    csr_correct_dterm=""
                
                # check_item=CheckItem("CHK03-OUT-LEAF")
                # check_item.outcome_level="FACT"
                # check_item.general_message="In the flowchart, this row reached leaf -->"
                # check_item.row_specific_message=(
                #     f"leaf {leaf}"
                #     )
                # this_row_analysis.append(check_item)
                
                
                if leaf in ["vi","vii"]:
                    did_term_type="a"
                    did_term_words="Description Id/Term"
                elif leaf in ["iv","v"]:
                    did_term_type="b"
                    did_term_words="Term"
                elif leaf in ["ii","x"]:
                    did_term_type="c"
                    did_term_words="Description Id"
                else:
                    did_term_type=None
                    did_term_words=None

                for outcome_code_digits in outcome_codes_matrix[leaf]:
                    # check_item=generate_check_item(outcome_code=f"CHK03-OUT-{outcome_code_digits}")
                    check_item=generate_check_item(
                        outcome_code=f"CHK03-OUT-{outcome_code_digits}",    
                        preferred_term=concepts[mr.C_Id].pt,
                        implied_concept_id=mr.C_Id, # only used in outcome_codes where this must be the *implied* C_Id
                        implied_dterm=mr.D_Term_derived_from_D_Id_entered,
                        dterm_type=dterm_type,
                        description_inactive=mr.D_Id_active=="0",
                        csr_correct_dterm=csr_correct_dterm,
                        data_entry_extract_type=setchks_session.data_entry_extract_type,
                        did_term_type=did_term_type,
                        did_term_words=did_term_words,
                        )
                    if check_item:
                        this_row_analysis.append(check_item)
                    if outcome_code_digits=="03" and mr.D_Id_active=="0":
                        n_INACTIVE_DESCRIPTION+=1
                    elif outcome_code_digits=="05":
                        if (dterm_type=="fsn" 
                            and setchks_session.data_entry_extract_type in ["ENTRY_PRIMARY","ENTRY_OTHER"]):
                            n_FSN_FOR_DATA_ENTRY+=1
                    elif outcome_code_digits=="06":
                        n_TERM_CONCEPT_MISMATCH+=1
                    elif outcome_code_digits=="07":
                        n_CAPITALISATION_ISSUE+=1
                    elif outcome_code_digits=="09":
                        n_TERM_DID_MISMATCH+=1

            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                #<check_item>
                check_item=CheckItem("CHK03-OUT-NOT_FOR_PRODUCTION")
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
            check_item=CheckItem("CHK03-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            #</check_item>
            this_row_analysis.append(check_item)
        
        #sort check_items in this_row_analysis
        def sorting_order(check_item):
            trimmed_outcome_code=check_item.outcome_code[:12] # get rid of final a,b,c
            order=[
                "CHK03-OUT-03",
                "CHK03-OUT-05",
                "CHK03-OUT-06",
                "CHK03-OUT-09",
                "CHK03-OUT-07",
                "CHK03-OUT-10",
                "CHK03-OUT-20",
                "CHK03-OUT-01",
                "CHK03-OUT-08",
                "CHK03-OUT-02",
                "CHK03-OUT-04",
                "CHK03-OUT-20",
                ]
            if trimmed_outcome_code in order:
                value=order.index(trimmed_outcome_code)
            else:
                value=99999
            # print(f"SORTING VALUE {trimmed_outcome_code} : {value}")
            return value
        this_row_analysis.sort(key=sorting_order)


    # assign CHK03-OUT-04 type check items depending on whether have see FSN misuse
    # in which case useful to see what all the other term types are
    # print("======================")
    for this_row_analysis in setchk_results.row_analysis:
        for check_item in this_row_analysis:
            if check_item.outcome_code in ["CHK03-OUT-04a","CHK03-OUT-04b","CHK03-OUT-04c"]:
                if n_FSN_FOR_DATA_ENTRY>0 and setchks_session.output_full_or_compact=="FULL_OUTPUT":
                    check_item.outcome_level="FACT"
                else:
                    check_item.outcome_level="DEBUG"
    
    n_ISSUES=( 
          n_INACTIVE_DESCRIPTION
        + n_FSN_FOR_DATA_ENTRY
        + n_TERM_CONCEPT_MISMATCH
        + n_CAPITALISATION_ISSUE
        + n_TERM_DID_MISMATCH
        + n_MISSING_TERM    # possibly should treat missing term separately
                            # as an AMBER issue and pssibly report two levels in 
                            # this check
        )
    
    if n_ISSUES==0 and n_MISSING_TERM==0:
        if setchks_session.columns_info.have_dterm_column:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        "[GREEN] This check has detected no issues."
                        ),
                    outcome_code="CHK03-OUT-12",
                    )
                )     
            #</set_level_message>
        else:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        "[GREEN] This check has detected no issues. Scope of check was limited, as no Term column was chosen."
                        ),
                    outcome_code="CHK03-OUT-21",
                    )
                )     
            #</set_level_message>
    


    if n_ISSUES!=0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[RED] This check has detected errors that need to be fixed."
                    ),
                outcome_code="CHK03-OUT-19",
                )
            )
        #</set_level_message>

        if n_INACTIVE_DESCRIPTION!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows with inactive Descriptions"
                    ),
                value=f"{n_INACTIVE_DESCRIPTION}",
                outcome_code="CHK03-OUT-13",
                )
            )
            #</set_level_count>
        if n_FSN_FOR_DATA_ENTRY!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows using a Fully Specified Name in this data "
                    "entry value set"
                    ),
                value=f"{n_FSN_FOR_DATA_ENTRY}",
                outcome_code="CHK03-OUT-14",
                )
            )
            #</set_level_count>
        if n_TERM_CONCEPT_MISMATCH!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows where the Term does not match the Concept"
                    ),
                value=f"{n_TERM_CONCEPT_MISMATCH}",
                outcome_code="CHK03-OUT-15",
                )
            )
            #</set_level_count>

        if n_TERM_DID_MISMATCH!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows where the Term does not match the Description Id"
                    ),
                value=f"{n_TERM_DID_MISMATCH}",
                outcome_code="CHK03-OUT-16",
                )
            )
            #</set_level_count>

        if n_CAPITALISATION_ISSUE!=0:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows where there is a capitalisation issue"
                    ),
                value=f"{n_CAPITALISATION_ISSUE}",
                outcome_code="CHK03-OUT-17",
                )
            )
            #</set_level_count>

    if n_MISSING_TERM!=0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[AMBER] Some entries are missing in the Term column. You may wish to correct this."
                    ),
                outcome_code="CHK03-OUT-11",
                )
            )
        #</set_level_message>
             
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows where the Term is missing"
                    ),
                value=f"{n_MISSING_TERM}",
                    outcome_code="CHK03-OUT-18",
                )
        )
        #</set_level_count>

