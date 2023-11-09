import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.set_refactoring.valset_module import ClauseMembershipAnalysis

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
            
    if setchks_session.refactored_form is None: # do refactoring if not already done
        original_valset, refactored_valset=refactor_core_code.refactor_core_code(
                    valset_extens_defn=value_set_members,
                    concepts=concepts,
                    ) 
        setchks_session.refactored_form=refactored_valset

# A pattern analysis of your value set indicates that you have 37 concepts that are all descendants of the concept X but there are 8 descendants that you have not included.
# These m concepts (that you may have omitted in error) are: ….  Overlap (I1,E1)+overlap(I1+E2)+overlap(I1+E3) …
# Additional part (of form):
# It may help you in your further analysis to know that this list of omissions contains all the 4 descendants (and self as case may be) 
# of Y (the root of E1):            only if overlap(I1,E1) = membership(E1)

    clauses=setchks_session.refactored_form.clause_based_rule.clauses

    include_clauses_and_memberships=[]
    exclude_clauses_and_memberships=[]
    all_excluded_concepts=set()

    for clause in clauses:
        members=ClauseMembershipAnalysis(clause=clause, concepts=concepts).members # members is a list of concept ids
        members=set(concepts[x] for x in members) # now members is a set of Concepts
        if clause.clause_type=="include":
            include_clauses_and_memberships.append((clause, members,))
        else:
            exclude_clauses_and_memberships.append((clause, members,))
            all_excluded_concepts.update(members)

    for i_clause, clause_and_members_tuple in enumerate(include_clauses_and_memberships):
        include_clause, include_members=clause_and_members_tuple
        members_excluded_from_this_include=include_members.intersection(all_excluded_concepts)
        if members_excluded_from_this_include==set():
            print(f"include clause {i_clause}:{include_clause.clause_string} is included in its entirety")
        else:
            print(f"")
            print(f"include clause {i_clause}:{include_clause.clause_string} has {len(members_excluded_from_this_include)} exclusions")
            print(f"these are:")
            for concept in members_excluded_from_this_include:
                print(f"{concept.concept_id} | {concept.pt} |")

    setchk_results.set_analysis["Messages"]=[]
    msg=(   
        f"Hello" 
        )
    setchk_results.set_analysis["Messages"].append(msg)

    