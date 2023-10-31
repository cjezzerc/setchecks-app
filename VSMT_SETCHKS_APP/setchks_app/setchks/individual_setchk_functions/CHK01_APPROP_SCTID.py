"""CHK01: Appropriate SNOMED CT identifiers for value set members 
"""
import os

def do_check(setchks_session=None, setchk_results=None):

    """
    Implements just the Core check
    """

    print("Set Check %s called" % setchk_results.setchk_code)


    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################

    # concept_id_col=setchks_session.cid_col
    ci=setchks_session.columns_info
    column_types=ci.column_types

    # initialise counters as used in the specification
    n_CID_ROWS=0
    n_DID_ROWS=0
    n_BLANK_ENTRY_ROWS=0
    n_UNEXPECTED_ENTRY_ROWS=0
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # with gatekeeper this is just blank or header rows

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        n_FILE_PROCESSABLE_ROWS+=1
        check_item={}
        if not mr.blank_row:
            if mr.C_Id_entered is not None: # CHK01-OUT-09 (CID)
                n_CID_ROWS+=1
                check_item={}
                check_item["Result_id"]=0 
                check_item["Message"]="OK"
            elif mr.D_Id_entered is not None: # CHK01-OUT-10 (DID)
                n_DID_ROWS+=1
                check_item={}
                check_item["Result_id"]=1 
                check_item["Message"]="""A Description Id value has been detected in the SNOMED Id column. 
It is recommended that value set members should be identified by Concept Ids. 
Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids.""" 
            else: # with gatekeeper this should never be reached
                check_item["Result_id"]=-1
                check_item["Message"]=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed
            check_item["Message"]="Blank line"
            check_item["Result_id"]=-2 # this flags a blank line
        setchk_results.row_analysis.append([check_item])
    

    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s in the MIXED column, of your input file of %s rows"
    
    msg=msg_format % (n_CID_ROWS, 'Concept IDs', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_DID_ROWS, 'Description IDs', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_UNEXPECTED_ENTRY_ROWS, 'unexpected values', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_BLANK_ENTRY_ROWS, 'blanks', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg="""Your input file contains a total of %s rows.
The system has assessed that %s rows could not be processed for this Set Check.
The system has processed %s rows for this Set Check.""" % (n_FILE_TOTAL_ROWS, n_FILE_NON_PROCESSABLE_ROWS, n_FILE_PROCESSABLE_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
