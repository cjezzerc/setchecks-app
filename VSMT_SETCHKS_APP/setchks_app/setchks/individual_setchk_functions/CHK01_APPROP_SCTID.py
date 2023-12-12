import os

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow

def do_check(setchks_session=None, setchk_results=None):

    """
    Implements just the Core check
    """

    print("Set Check %s called" % setchk_results.setchk_code)


    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################

    # initialise counters as used in the specification
    n_CID_ROWS=0
    n_DID_ROWS=0
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # with gatekeeper this is just blank or header rows

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        n_FILE_PROCESSABLE_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            if mr.C_Id_entered is not None: 
                n_CID_ROWS+=1
                check_item=CheckItem("CHK01-OUT-01")
                check_item.general_message="OK"
                check_item.outcome_level="INFO"
                this_row_analysis.append(check_item)
            elif mr.D_Id_entered is not None: 
                n_DID_ROWS+=1
                if setchks_session.data_entry_extract_type in ["EXTRACT"]:
                    check_item=CheckItem("CHK01-OUT-03")
                    check_item.general_message=(
                        "A Description Id value has been detected in the MIXED column of this "
                        "data extract value set. "
                        "Description Ids should NEVER be used in data extract value sets"
                        )
                    this_row_analysis.append(check_item)
                else:
                    check_item=CheckItem("CHK01-OUT-02")
                    check_item.general_message=(
                        "A Description Id value has been detected in the MIXED column. "
                        "It is recommended that value set members should be identified by Concept Ids. "
                        "Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids."
                        )
                    this_row_analysis.append(check_item)
            else: 
                pass
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed
            check_item=CheckItem("CHK01-OUT-BLANK_ROW")
            check_item.general_message="Blank line"
            check_item.outcome_level="INFO"
            this_row_analysis.append(check_item)
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    
    setchk_results.set_level_table_rows=[]
    
    if n_DID_ROWS==0:
        setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        "[GREEN] No issues have been detected "
                        ),
                    )
                )

    else: # Issue varying levels of admonition if any Description Ids have been used
        if setchks_session.data_entry_extract_type in ["EXTRACT"]:
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    simple_message=(
                        "[RED] At least one Description Id has been detected "
                        "in the MIXED column for this data extraction value set. "
                        "This is a serious error. Data extraction value sets should ONLY contain Concept Ids"
                        ),
                    )
                )

        else:
            if n_CID_ROWS!=0: 
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                        simple_message=(
                            "[AMBER] A mixture of Concept Ids and Description Ids has been detected "
                            "in the MIXED column for this value set. This situation should be avoided. "
                            "Unless it is vital for your use case, we strongly recommend replacing the Description Ids with " 
                            "the corresponding Concept Ids"
                            ),
                        )
                    )
            else:            
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                        simple_message=(
                            "[AMBER] Your data entry value set contains exclusively Description Ids "
                            "in the MIXED column for this value set."
                            "Unless it is vital for your use case, we recommend replacing all the Ids with "
                            "the corresponding Concept Ids"
                            ),
                        )
                    )
 
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing Concept Ids in the MIXED column of your input file " 
                    ),
                value=f"{n_CID_ROWS}",
                )
        )

        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    f"Number of rows containing Description Ids in the MIXED column of your input file " 
                    ),
                value=f"{n_DID_ROWS}",
                )
        )

    
