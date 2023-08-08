"""Check for concepts that are in the Default Exclusion Filter Refset
"""

def do_check(setchks_session=None, setchk_results=None):

    """
    Limitations:
    1) Assumes a cid_column has been defined and contents are all concept ids (ie doe no inferring of cid from did)
    2) Assumes all data rows (apart from header if has one) contain a cid; ie does not hadnle blank rows well
    """

    print("Set Check %s called" % setchk_results.setchk_name)

    ##################################################################
    ##################################################################
    ##################################################################
    # Fetch and process membership of refset from Terminology Server #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    # Fetch membership of default exclusion filter refset
    # ** Assumes this refset will never be large enough to require paging
    default_exclusion_filter_refset_id=999002571000000104
    refset_response=setchks_session.terminology_server.do_expand(refset_id=default_exclusion_filter_refset_id, sct_version=setchks_session.sct_version, add_display_names=True)

    # Convert response into a dictionary of display strings keyed by concept_id
    # and a set of concept_ids
    # ** Really should make the data returned by terminology_server.do_expand be less string based 
    refset_concept_ids=set()
    refset_displays={}
    for response_string in refset_response:
        f=[x.strip() for x in response_string.split("|")]
        concept_id, display, active_indication=f
        refset_concept_ids.add(concept_id)
        refset_displays[concept_id]=display
    
    ##################################################################
    ##################################################################
    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################
    ##################################################################
    ##################################################################
    
    concept_id_col=setchks_session.cid_col
    n_set_members_in_refset=0
    print("=============>>>>>>>>>>>>>>>>>>>>>>>", setchks_session.table_has_header, setchks_session.first_data_row)
    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        concept_id=row[concept_id_col] # ** Need to know from precheck if row is a valid row. For now assume all rows contain CID related data
        row_analysis={}
        if concept_id in refset_concept_ids:
            row_analysis["Result_id"]=2 # ** How generalisable is concept of a enumerated result_id across the suite of checks?
            row_analysis["Message"]="Concept is in the Default Exclusion Filter; (Preferred Term = '%s')" % refset_displays[concept_id]
            n_set_members_in_refset+=1 # ** ?This could be generalised to how many give each result_id
        else:
            row_analysis["Result_id"]=1
            row_analysis["Message"]="OK"
        

        setchk_results.row_analysis.append(row_analysis)

    setchk_results.set_analysis["n_set_members_in_refset"]=n_set_members_in_refset   # ** ?This could be generalised
    setchk_results.set_analysis["Message"]="Guess what? %s of the members of your value set are in the Default Exclusion Reference Set" % n_set_members_in_refset