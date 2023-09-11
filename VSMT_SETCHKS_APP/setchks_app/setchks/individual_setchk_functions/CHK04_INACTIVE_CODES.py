"""Finds the active status of the concept on each row

"""

import os
import vsmt_uprot.terminology_server_module

def do_check(setchks_session=None, setchk_results=None):

    # print("SLEEPING")
    # import time; time.sleep(20)
    # print("AWAKE")

    # concept_id_col=setchks_session.cid_col
    concept_id_col=setchks_session.columns_info.cid_column
    concept_ids_list=[]

    ##############################
    #                            #
    # grab a list of concept_ids #
    #                            #
    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        concept_ids_list.append(row[concept_id_col].string)
    #                            #
    ##############################

    print(concept_ids_list)

    ####################################################
    #                                                  #
    # Generate ECL statement corresponding to the list #
    #                                                  #
    ecl=" OR ".join([x for x in concept_ids_list])
    #                                                  #
    ####################################################

    ####################
    # Expand ECL       #
    #                  #
    
    # really should check for when token expires first but that did not seem to be working
    setchks_session.terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                            auth_url=os.environ["ONTOAUTH_INSTANCE"])
    refset_response=setchks_session.terminology_server.do_expand(ecl=ecl, 
                                                                 sct_version=setchks_session.sct_version.formal_version_string, 
                                                                 add_display_names=True,
                                                                 )

    # Convert response into a dictionary of display strings keyed by concept_id
    # and a set of concept_ids
    # ** Really should make the data returned by terminology_server.do_expand be less string based 
    active_status_dict={}
    for response_string in refset_response:
        f=[x.strip() for x in response_string.split("|")]
        concept_id, display, active_indication=f
        active_status_dict[concept_id]=  active_indication=='(inactive=None)'
    #                  #
    ####################

    #########################
    #                       #
    # Generate row analysis #
    #                       #
    n_processed=0
    n_active=0
    n_inactive=0
    n_not_found=0
    for i_row, row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):

        n_processed+=1
        check_item={}
        
        # concept_id=row[concept_id_col].parsed_sctid.sctid_string
        concept_id=row[concept_id_col].string

        if concept_id in active_status_dict:
            active_status=active_status_dict[concept_id]
        else:
            active_status=None

        if active_status is True:
            check_item["Result_id"]=1
            check_item["Message"]="Concept is active"
            n_active+=1
        elif active_status is False:
            check_item["Result_id"]=2
            check_item["Message"]="Concept is INACTIVE"
            n_inactive+=1
        else:
            check_item["Result_id"]=3
            check_item["Message"]="Concept could not be found in the specified release"
            n_not_found+=1
        
        setchk_results.row_analysis.append([check_item])
    #                       #
    #########################

    #############################
    #                           #
    #   Generate set analysis   #
    #                           #
    setchk_results.set_analysis["Message"]= "The value set has %s inactive concepts (tot=%s;active=%s;not_found=%s)" % (n_inactive,
                                                                                                                            n_processed,
                                                                                                                            n_active,
                                                                                                                            n_not_found)
    #                           #
    #############################
