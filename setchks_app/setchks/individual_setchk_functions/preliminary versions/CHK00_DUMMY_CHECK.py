"""A dummy check that just puts in placeholder messages
"""

def do_check(setchks_session=None, setchk_results=None):

    ##################################################################
    ##################################################################
    ##################################################################
    #          Dummy test concept on each row of value set           #     
    ##################################################################
    ##################################################################
    ##################################################################
    
    concept_id_col=setchks_session.cid_col
    n_set_members_in_refset=0
    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        row_analysis={}
        
        row_analysis["Result_id"]=1
        row_analysis["Message"]="Dummy row message"
        
        setchk_results.row_analysis.append(row_analysis)

    setchk_results.set_analysis["Message"]="This is a dummy message. The set has %s rows" % len(setchks_session.data_as_matrix)