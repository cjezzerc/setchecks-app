import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService

from ..check_item import CheckItem


       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it can be called for all data_entry_extract_types
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    ##################################################################
    ##################################################################
    ##################################################################
    # Refactor value set                                             #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    value_set_members=set()
    
    for mr in setchks_session.marshalled_rows:
        concept_id=mr.C_Id
        if concept_id is not None:
            value_set_members.add(concept_id)
            
    original_valset, refactored_valset=refactor_core_code.refactor_core_code(
                valset_extens_defn=value_set_members,
                concepts=concepts,
                ) 
    
    setchks_session.refactored_form=refactored_valset

    setchk_results.set_analysis["Messages"]=[]
    msg=(   
        f"Refactored form:" 
        )
    setchk_results.set_analysis["Messages"].append(msg)

    n_INCLUDE_CLAUSES=0
    n_EXCLUDE_CLAUSES=0
    for clause in refactored_valset.clause_based_rule.clauses:
        clause_base_concept_id=str(clause.clause_base_concept_id)
        clause_type=clause.clause_type
        if clause_type=="include":
            n_INCLUDE_CLAUSES+=1
        else:
            n_EXCLUDE_CLAUSES+=1
        clause_operator=clause.clause_operator
        if clause_operator[0]=="=":
            clause_operator=clause_operator[1:]
        pt=concepts[clause_base_concept_id].pt
        msg=(
            f"{clause_type} {clause_operator:2} {clause_base_concept_id:20} {pt}"
            )
        setchk_results.set_analysis["Messages"].append(msg)     
        
    
    msg=(
    f"There are {n_INCLUDE_CLAUSES} include clauses in the refactored form "  
    )
    setchk_results.set_analysis["Messages"].append(msg)


    msg=(
    f"There are {n_EXCLUDE_CLAUSES} exclude clauses in the refactored form "  
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    n_CLAUSES=n_INCLUDE_CLAUSES+n_EXCLUDE_CLAUSES
    msg=(
    f"There are {n_CLAUSES} clauses in total in the refactored form "  
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    if n_CLAUSES>30:
        msg=(
        "There are more than 30 clauses in the refactored form. "
        "This suggests that either you ahave a very scattered set of clauses, or "
        "that you are trying to cover too large an scope with one value set"
        )
        setchk_results.set_analysis["Messages"].append(msg)
    