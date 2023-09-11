"""CHK20: Incorrectly formatted SNOMED CT identifiers 
"""
import os

import vsmt_uprot.terminology_server_module

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
    n_OUTCOME_ROWS={}    
    n_NO_OUTCOME_ROWS={}    
    for col_type in ["ALL","CID","DID","MIXED"]:
        n_OUTCOME_ROWS[col_type] =0
        n_NO_OUTCOME_ROWS[col_type] =0
    FILE_TOTAL_ROWS=0       # this definition still to be finalised
    FILE_PROCESSABLE_ROWS=0 # this definition still to be finalised
    FILE_UNPROCESSABLE_ROWS=0 # this definition still to be finalised

    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        FILE_TOTAL_ROWS+=1       
        FILE_PROCESSABLE_ROWS+=1 
        row_analysis=[]
        outcome_seen_this_row=False
        for i_cell, cell in enumerate(row):
            col_type=column_types[i_cell]
            if col_type in ["CID", "DID", "MIXED"]: # only check in these types of column
                if cell.parsed_sctid.valid: # CHK20-OUT-01 (Valid SCTID)
                    n_NO_OUTCOME_ROWS[col_type]+=1
                    check_item={}
                    check_item["Result_id"]=0 
                    check_item["Message"]="OK"
                    row_analysis.append(check_item)
                elif cell.parsed_sctid.sctid_string=="": # CHK20-OUT-O2 (blank cell)
                    outcome_seen_this_row=True
                    n_OUTCOME_ROWS[col_type]+=1
                    check_item={}
                    check_item["Result_id"]=1 
                    check_item["Message"]="""
The identifier in the %s column was not checked against the definition for a SNOMED identifier as no value was provided. 
"""                     % column_types[i_cell] 
                    row_analysis.append(check_item)
                else: # CHK20-OUT-03  (invalid SCTID)
                    outcome_seen_this_row=True
                    n_OUTCOME_ROWS[col_type]+=1
                    check_item={}
                    check_item["Result_id"]=2 
                    check_item["Message"]="""
The identifier in the %s column does not meet the definition for a SNOMED identifier. 
It should not be should not be used for recording information in a patient record.
It can never be extracted from a patient record (as it should never be recorded in the first place). 
We strongly recommend that you amend your value set to replace (or remove) this malformed SNOMED identifier from your value set.
"""                     % column_types[i_cell]
                    row_analysis.append(check_item)
        if outcome_seen_this_row:
            n_OUTCOME_ROWS['ALL']+=1
        else:
            n_NO_OUTCOME_ROWS['ALL']+=1
        setchk_results.row_analysis.append(row_analysis)

    ##################################################################
    #     Generate set(file) level analysis                          #     
    ##################################################################

    setchk_results.set_analysis["Messages"]=[] 
    msg_format="There are %s rows containing %s formatted SNOMED CT identifiers %s input file of %s rows"
    
    if ci.have_both_cid_and_did_columns:
        msg=msg_format % (n_OUTCOME_ROWS["ALL"], 'one or more incorrectly', 'in your', FILE_TOTAL_ROWS)
        setchk_results.set_analysis["Messages"].append(msg)
        msg=msg_format % (n_NO_OUTCOME_ROWS["ALL"], 'correctly', 'in your', FILE_TOTAL_ROWS)
        setchk_results.set_analysis["Messages"].append(msg)
    
    for short_form, long_form in { "CID":"Concept Id", "DID":"Description Id", "MIXED": "Mixed Id"}.items():
        if short_form in column_types:
            msg=msg_format % (n_OUTCOME_ROWS[short_form], 'incorrectly', 'in the ' + long_form + ' column of your', FILE_TOTAL_ROWS)
            setchk_results.set_analysis["Messages"].append(msg)
            msg=msg_format % (n_NO_OUTCOME_ROWS[short_form], 'correctly', 'in the ' + long_form + ' column of your', FILE_TOTAL_ROWS)
            setchk_results.set_analysis["Messages"].append(msg)

    msg="""
Your input file contains a total of %s rows.
The system has assessed that %s rows could not be processed for this Set Check.
The system has processed %s rows for this Set Check. 
""" % (FILE_TOTAL_ROWS, FILE_UNPROCESSABLE_ROWS, FILE_PROCESSABLE_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
