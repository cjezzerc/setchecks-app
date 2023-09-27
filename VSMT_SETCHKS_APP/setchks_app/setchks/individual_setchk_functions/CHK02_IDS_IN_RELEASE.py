"""Check for concepts that are in the Default Exclusion Filter Refset
"""
import os

import logging
logger=logging.getLogger()

import vsmt_uprot.terminology_server_module

def do_check(setchks_session=None, setchk_results=None):

    """
    """

    
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # this is just blank or header rows
    
    n_CID_NISR=0
    n_CID_ISR=0
    n_CID_NILR=0
    n_CID_ILR=0
    n_DID_NISR=0
    n_DID_ISR=0
    n_DID_NILR=0
    n_DID_NILR=0

    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        check_item={}
        if not mr.blank_row:
            n_FILE_PROCESSABLE_ROWS+=1
            
#             if concept_id is not None:
#                 if concept_id in refset_concept_ids: # CHK06-OUT-01
#                     n_OUTCOME_IN_EXCL_REF_SET+=1
#                     check_item["Result_id"]=1 # ** How generalisable is concept of a enumerated result_id across the suite of checks?
#                     check_item["Message"]="""This concept is not recommended for use within a patient record, i.e., is not recommended for clinical data entry.
# Please replace this concept. 
# We recommend you visit termbrowser.nhs.uk to identify a more suitable term"""
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows
            check_item["Message"]="Blank line"
            check_item["Result_id"]=-2 # this flags a blank line
        setchk_results.row_analysis.append([check_item])


    setchk_results.set_analysis["Messages"]=[] 
    
    msg_format="There are %s rows where the concept was assessed %s for use as part of this value set, in your input file of  %s rows"
    msg=msg_format % (n_OUTCOME_IN_EXCL_REF_SET, 'as not recommended', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    msg=msg_format % (n_NO_OUTCOME_EXCL_REF_SET, 'as permissible', n_FILE_TOTAL_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg="""Your input file contains a total of %s rows.
The system has assessed that %s rows could not be processed for this Set Check (blank or header rows).
The system has assessed %s rows for this Set Check.""" % (n_FILE_TOTAL_ROWS, n_FILE_NON_PROCESSABLE_ROWS, n_FILE_PROCESSABLE_ROWS)
    setchk_results.set_analysis["Messages"].append(msg)