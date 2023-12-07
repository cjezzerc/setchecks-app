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
        n_FILE_PROCESSABLE_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis updated below, 
        if not mr.blank_row:
            if mr.C_Id_why_none=="INVALID_SCTID":
                n_OUTCOME_ROWS+=1
                check_item=CheckItem("CHK20-OUT-01")
                check_item.general_message=(
                    "The identifier in the MIXED column does not meet the definition for a SNOMED identifier. "
                    "It should not be used for recording information in a patient record. "
                    "It can never be extracted from a patient record "
                    "(as it should never be recorded in the first place)." 
                    "We strongly recommend that you amend your value set to replace (or remove) "
                    "this malformed SNOMED identifier from your value set."
                    )
                this_row_analysis.append(check_item)
            elif mr.C_Id_why_none=="BLANK_ENTRY": # CHK20-OUT-O2 (blank cell)
                n_OUTCOME_ROWS+=1
                check_item=CheckItem("CHK20-OUT-03")
                check_item.general_message=(
                    "The identifier in the MIXED column was not checked against the definition " 
                    "for a SNOMED identifier as no value was provided."
                    ) 
                this_row_analysis.append(check_item)
            else: # CHK20-OUT-01 (Valid SCTID)
                n_NO_OUTCOME_ROWS+=1
                check_item=CheckItem("CHK20-OUT-02")
                check_item.outcome_level="INFO"
                check_item.general_message="OK"
                this_row_analysis.append(check_item)
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed
            check_item=CheckItem("CHK20-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)

        if mr.excel_corruption_suspected and mr.possible_reconstructed_C_Id is not None:
            
            check_item=CheckItem("CHK20-OUT-04")
            check_item.general_message=(
                f"It appears that this ID could have been corrupted by Excel, and if "
                f"so could be reconstructed as the Concept ID -->"
            )
            check_item.row_specific_message=(termbrowser_hyperlink(mr.possible_reconstructed_C_Id))
            this_row_analysis.append(check_item)

            check_item=CheckItem("CHK20-OUT-05")
            check_item.general_message=(
                f"The preferred term for this reconstructed Concept Id is --> "
            )
            check_item.row_specific_message=concepts[mr.possible_reconstructed_C_Id].pt
            this_row_analysis.append(check_item)

        if mr.excel_corruption_suspected and mr.possible_reconstructed_D_Id is not None:
            
            check_item=CheckItem("CHK20-OUT-06")
            check_item.general_message=(
                f"It appears that this ID could have been corrupted by Excel, and if "
                f"so could be reconstructed as the Concept ID -->"
            )
            check_item.row_specific_message=(termbrowser_hyperlink(mr.possible_reconstructed_D_Id))
            this_row_analysis.append(check_item)

            D_Id_data=ds.get_data_about_description_id(
                    description_id=mr.possible_reconstructed_D_Id, 
                    sct_version=setchks_session.sct_version
                    )
            if D_Id_data is not None: 
                term=D_Id_data["term"]
            else:
                term="Not found"
            check_item=CheckItem("CHK20-OUT-07")
            check_item.general_message=(
                f"The term for this reconstructed Description Id is --> "
            )
            check_item.row_specific_message=(term)
            this_row_analysis.append(check_item)            
           
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s formatted SNOMED CT identifiers in input file of %s rows"
    
    msg=msg_format % (n_OUTCOME_ROWS, 'incorrectly', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    msg=msg_format % (n_NO_OUTCOME_ROWS, 'correctly', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)

    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor="Number of rows containing incorrectly formatted SNOMED CT identifiers",
            value=n_OUTCOME_ROWS,
            )
        )
    
    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)


