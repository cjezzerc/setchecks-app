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
                    "The entry in the Identifier column does not conform to the SCTID data type. "
                    "This entry must be removed or corrected for the full suite of Set Checks to be performed."
                    )
                #</check_item>
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": 
                n_OUTCOME_ROWS+=1
                #<check_item>
                check_item=CheckItem("CHK20-OUT-03")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "The Identifier column is blank. "
                    "The entry must be populated or the row removed. "
                    ) 
                #</check_item>
                this_row_analysis.append(check_item)
            else: 
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
                f"It appears that your entry in the Identifier column may have been previously corrupted by Excel. If "
                f"so, this check suggests that the original intent was to include Concept Id -->"
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
                f"The Preferred Term for the suggested Concept Id is --> "
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
                f"It appears that your entry in the Identifier column may have been previously corrupted by Excel. If "
                f"so, this check suggests that the original intent was to include Description Id -->"
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
                f"The Term for the suggested Description Id is --> "
            )
            check_item.row_specific_message=(
                term
                )
            #</check_item>
            this_row_analysis.append(check_item)            
        
        #sort check_items in this_row_analysis
        def sorting_order(check_item):
            trimmed_outcome_code=check_item.outcome_code[:12] # get rid of final a,b,c
            order=[
                "CHK20-OUT-01",
                "CHK20-OUT-03",
                "CHK20-OUT-04",
                "CHK20-OUT-06",
                "CHK20-OUT-05",
                "CHK03-OUT-07",
                ]
            if trimmed_outcome_code in order:
                value=order.index(trimmed_outcome_code)
            else:
                value=99999
            # print(f"SORTING VALUE {trimmed_outcome_code} : {value}")
            return value
        this_row_analysis.sort(key=sorting_order)       
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 

    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
            "Total number of rows in the input file"
            ),
            value=n_FILE_TOTAL_ROWS,
            outcome_code="CHK20-OUT-10"
            )
        )
    #</set_level_count>
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows NOT assessed in the input file "
                "(header rows or entirely blank rows)"
                ),
            value=n_FILE_NON_PROCESSABLE_ROWS,
            outcome_code="CHK20-OUT-11"
            )
        )
    #</set_level_count>
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows assessed in the input file"
                ),
            value=n_FILE_PROCESSABLE_ROWS,
            outcome_code="CHK20-OUT-12"
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
                    "[RED] Your value set contains entries that do not conform to the SCTID data type. " 
                    "These entries must be corrected "
                    "for the full suite of Set Checks to be performed."
                    ),
                outcome_code="CHK20-OUT-09",
                )
            )        
        #</set_level_message>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of conforming rows"
                    ),
                value=n_NO_OUTCOME_ROWS,
                outcome_code="CHK20-OUT-13",
                )
            )
        #</set_level_count>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of non-conforming rows"
                    ),
                value=n_OUTCOME_ROWS,
                outcome_code="CHK20-OUT-14",
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


