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
            if mr.C_Id_entered is not None: # CHK01-OUT-09 (CID)
                n_CID_ROWS+=1
                check_item=CheckItem("CHK01-OUT-09")
                check_item.general_message="OK"
                check_item.outcome_level="INFO"
                this_row_analysis.append(check_item)
            elif mr.D_Id_entered is not None: # CHK01-OUT-10 (DID)
                n_DID_ROWS+=1
                check_item=CheckItem("CHK01-OUT-10")
                check_item.general_message=(
                    "A Description Id value has been detected in the MIXED column. "
                    "It is recommended that value set members should be identified by Concept Ids. "
                    "Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids."
                    )
                this_row_analysis.append(check_item)
            else: # with gatekeeper this should never be reached
                check_item=CheckItem("CHK01-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                this_row_analysis.append(check_item)
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed
            check_item=CheckItem("CHK01-OUT-BLANK_ROW")
            check_item.general_mesage="Blank line"
            check_item.outcome_level="INFO"
            this_row_analysis.append(check_item)
    
    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s in the MIXED column, of your input file of %s rows"
    
    msg=msg_format % (n_CID_ROWS, 'Concept IDs', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_DID_ROWS, 'Description IDs', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has assessed that {n_FILE_NON_PROCESSABLE_ROWS} rows could not be processed for this Set Check.\n"
        f"The system has processed {n_FILE_PROCESSABLE_ROWS} rows for this Set Check.")
    setchk_results.set_analysis["Messages"].append(msg)
