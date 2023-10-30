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
    FILE_TOTAL_ROWS=0       # this definition still to be finalised
    FILE_PROCESSABLE_ROWS=0 # this definition still to be finalised
    FILE_NON_PROCESSABLE_ROWS=0 # this definition still to be finalised

    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        FILE_TOTAL_ROWS+=1       
        FILE_PROCESSABLE_ROWS+=1 
        row_analysis=[]
        for i_cell, cell in enumerate(row):
            col_type=column_types[i_cell]
            # if col_type in ["CID", "DID", "MIXED"]: # only check in these types of column
            if col_type in ["MIXED"]: # only check in these types of column
                if cell.parsed_sctid.component_type=="Concept_Id": # CHK01-OUT-09 (CID)
                    n_CID_ROWS+=1
                    check_item={}
                    check_item["Result_id"]=0 
                    check_item["Message"]="OK"
                    row_analysis.append(check_item)
                elif cell.parsed_sctid.component_type=="Description_Id": # CHK01-OUT-10 (CID)
                    n_DID_ROWS+=1
                    check_item={}
                    check_item["Result_id"]=1 
                    check_item["Message"]="""A Description Id value has been detected in the SNOMED Id column. 
It is recommended that value set members should be identified by Concept Ids. 
Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids.""" 
                    row_analysis.append(check_item)
                elif cell.parsed_sctid.sctid_string=="": # CHK20-OUT-12 (blank cell)
                    n_BLANK_ENTRY_ROWS+=1
                    check_item={}
                    check_item["Result_id"]=3 
                    check_item["Message"]="""An entry is missing in the Mixed Id column.
It is recommended that value set members should be identified by Concept Ids.
Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids.
If continuing to use a single column of Mixed Ids, consider populating it with a Concept Id or a Description Id."""
                    row_analysis.append(check_item)
                else: # CHK01-OUT-11 (CID)
                    n_UNEXPECTED_ENTRY_ROWS+=1
                    check_item={}
                    check_item["Result_id"]=4 
                    check_item["Message"]="""An unexpected value has been detected in the Mixed Id column.
It is recommended that value set members should be identified by Concept Ids.
Consider using a single column identifier of Concept Ids instead of a single column of Mixed Ids.
If continuing to use a single column of Mixed Ids, consider replacing the unexpected value with a Concept Id or a Description Id."""
                    row_analysis.append(check_item)
        setchk_results.row_analysis.append(row_analysis)

    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s in the MIXED column, of your input file of %s rows"
    
    msg=msg_format % (n_CID_ROWS, 'Concept IDs', FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_DID_ROWS, 'Description IDs', FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_UNEXPECTED_ENTRY_ROWS, 'unexpected values', FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=msg_format % (n_BLANK_ENTRY_ROWS, 'blanks', FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg="""Your input file contains a total of %s rows.
The system has assessed that %s rows could not be processed for this Set Check.
The system has processed %s rows for this Set Check.""" % (FILE_TOTAL_ROWS, FILE_NON_PROCESSABLE_ROWS, FILE_PROCESSABLE_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
