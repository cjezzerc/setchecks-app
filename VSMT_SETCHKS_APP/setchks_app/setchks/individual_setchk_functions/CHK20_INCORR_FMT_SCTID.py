"""CHK20: Incorrectly formatted SNOMED CT identifiers 
"""


import vsmt_uprot.terminology_server_module

import os
def do_check(setchks_session=None, setchk_results=None):

    """
    Implements just the Core check
    """

    print("Set Check %s called" % setchk_results.setchk_code)

    ##################################################################
    ##################################################################
    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################
    ##################################################################
    ##################################################################
    
    # concept_id_col=setchks_session.cid_col
    column_types=setchks_session.columns_info.cid_column.column_types
    
    n_set_members_in_refset=0
    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        for i_cell, cell in row:
            if column_types[i_cell] in ["CID", "DID", "MIXED"]:
                if cell.valid:
                    setchk_results.row_analysis.append({})
                else:
                    row_analysis={}
                    row_analysis["Result_id"]=1 # ** How generalisable is concept of a enumerated result_id across the suite of checks?
                    row_analysis["Message"]="""
                        The identifier in the %s column does not meet the definition for a SNOMED identifier. 
                        It should not be should not be used for recording information in a patient record.
                        It can never be extracted from a patient record (as it should never be recorded in the first place). 
                        We strongly recommend that you amend your value set to replace (or remove) this malformed SNOMED identifier from your value set.
                        """ % column_types[i_cell]
                    setchk_results.row_analysis.append(row_analysis)

    setchk_results.set_analysis["Message"]="TBI" 