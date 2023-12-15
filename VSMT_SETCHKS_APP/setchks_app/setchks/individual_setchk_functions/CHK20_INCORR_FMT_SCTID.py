import os

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow
from setchks_app.excel.termbrowser import termbrowser_hyperlink
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService


def do_check(setchks_session=None, setchk_results=None):

    """
    Implements just the Core check
    """

    print("Set Check %s called" % setchk_results.setchk_code)

    ds=DescriptionsService()
    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)
    
    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################

    # initialise counters as used in the specification
    n_OUTCOME_ROWS=0
    n_NO_OUTCOME_ROWS=0 

    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # with gatekeeper this is just blank or header rows

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis updated below, 
        if not mr.blank_row:
            n_FILE_PROCESSABLE_ROWS+=1
            if mr.C_Id_why_none=="INVALID_SCTID":
                n_OUTCOME_ROWS+=1
                #<check_item>
                check_item=CheckItem("CHK20-OUT-01")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The entry in the identifier column does not meet the definition for a SNOMED Identifier. "
                    "This entry must be removed or corrected for the full set of Set Checks to be performed."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": # CHK20-OUT-O2 (blank cell)
                n_OUTCOME_ROWS+=1
                #<check_item>
                check_item=CheckItem("CHK20-OUT-03")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The identifier column is blank and is treated as an incorrectly formatted entry. "
                    "The entry must be populated or the row removed. "
                    ) 
                #</check_item>
                this_row_analysis.append(check_item)
            else: # CHK20-OUT-01 (Valid SCTID)
                n_NO_OUTCOME_ROWS+=1
                #<check_item>
                check_item=CheckItem("CHK20-OUT-02")
                check_item.outcome_level="DEBUG"
                check_item.general_message="OK"
                #</check_item>
                this_row_analysis.append(check_item)
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed
            #<check_item>
            check_item=CheckItem("CHK20-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            #</check_item>
            this_row_analysis.append(check_item)

        if mr.excel_corruption_suspected and mr.possible_reconstructed_C_Id is not None:
            
            #<check_item>
            check_item=CheckItem("CHK20-OUT-04")
            check_item.outcome_level="ISSUE"
            check_item.general_message=(
                f"It appears that this Id could have been corrupted by Excel, and if "
                f"so could be reconstructed as the Concept Id -->"
            )
            check_item.row_specific_message=(
                termbrowser_hyperlink(mr.possible_reconstructed_C_Id)
                )
            #</check_item>
            this_row_analysis.append(check_item)

            #<check_item>
            check_item=CheckItem("CHK20-OUT-05")
            check_item.outcome_level="FACT"
            check_item.general_message=(
                f"The Preferred Term for this reconstructed Concept Id is --> "
            )
            check_item.row_specific_message=(
                concepts[mr.possible_reconstructed_C_Id].pt
                )
            #</check_item>
            this_row_analysis.append(check_item)

        if mr.excel_corruption_suspected and mr.possible_reconstructed_D_Id is not None:
            
            #<check_item>
            check_item=CheckItem("CHK20-OUT-06")
            check_item.outcome_level="ISSUE"
            check_item.general_message=(
                f"It appears that this Id could have been corrupted by Excel, and if "
                f"so could be reconstructed as the Description Id -->"
            )
            check_item.row_specific_message=(
                termbrowser_hyperlink(mr.possible_reconstructed_D_Id)
                )
            #</check_item>
            this_row_analysis.append(check_item)

            D_Id_data=ds.get_data_about_description_id(
                    description_id=mr.possible_reconstructed_D_Id, 
                    sct_version=setchks_session.sct_version
                    )
            if D_Id_data is not None: 
                term=D_Id_data["term"]
            else:
                term="Not found"
            #<check_item>
            check_item=CheckItem("CHK20-OUT-07")
            check_item.outcome_level="FACT"
            check_item.general_message=(
                f"The Term for this reconstructed Description Id is --> "
            )
            check_item.row_specific_message=(
                term
                )
            #</check_item>
            this_row_analysis.append(check_item)            
           
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 

    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
            "Number of rows in input file"
            ),
            value=n_FILE_TOTAL_ROWS,
            outcome_code="CHK20-OUT-XXX"
            )
        )
    #</set_level_count>
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows NOT assessed in input file "
                "(header rows or entirely blank rows)"
                ),
            value=n_FILE_NON_PROCESSABLE_ROWS,
            outcome_code="CHK20-OUT-XXX"
            )
        )
    #</set_level_count>
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows assessed in input file"
                ),
            value=n_FILE_PROCESSABLE_ROWS,
            outcome_code="CHK20-OUT-XXX"
            )
        )
    #</set_level_count>
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                ""
                ),
            value="",
            outcome_code="CHK20-OUT-DIVIDER"
            )
        )
    #</set_level_count>
    
    if n_OUTCOME_ROWS!=0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    f"[RED] This check has found issues that must be corrected "
                    f"for the full complement of Set Checks to be performed."
                    ),
                outcome_code="CHK20-OUT-07",
                )
            )        
        #</set_level_message>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows containing correctly formatted entries "
                    "in the Identifier Column"
                    ),
                value=n_NO_OUTCOME_ROWS,
                outcome_code="CHK20-OUT-05",
                )
            )
        #</set_level_count>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of rows containing incorrectly formatted entries "
                    "in the Identifier column"
                    ),
                value=n_OUTCOME_ROWS,
                outcome_code="CHK20-OUT-04",
                )
            )
        #</set_level_count>
        
    else:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    f"[GREEN] This check has detected no issues."
                    ),
                outcome_code="CHK20-OUT-08",
                )
            )
        #</set_level_message>


