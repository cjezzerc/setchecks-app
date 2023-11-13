import os

from ..check_item import CheckItem

def do_check(setchks_session=None, setchk_results=None):

    """
    Implements just the Core check
    """

    print("Set Check %s called" % setchk_results.setchk_code)

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

        # setchk_results.row_analysis.append([check_item])
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s formatted SNOMED CT identifiers in input file of %s rows"
    
    msg=msg_format % (n_OUTCOME_ROWS, 'incorrectly', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    msg=msg_format % (n_NO_OUTCOME_ROWS, 'correctly', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)


