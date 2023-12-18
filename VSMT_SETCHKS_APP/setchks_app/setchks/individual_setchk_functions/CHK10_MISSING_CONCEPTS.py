import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.set_refactoring.valset_module import ClauseMembershipAnalysis

from ..set_level_table_row import SetLevelTableRow
from ..chk_specific_sheet import ChkSpecificSheet, ChkSpecificSheetRow


       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it can be called for all data_entry_extract_types
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    plain_english_operators_fmts={
        "=":"Just %s ",
        "<":"All the descendants of %s (but not including itself)",
        "<<":"All the descendants of %s (including itself)",
        }
    
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
            
    # disable caching of refactored form as would have to be done differently since if running a batch of setchks in redis queue then
    # updates to setchks_session will be lost. Would have to run things like refactoring in a "pre" job
    # if setchks_session.refactored_form is None: # do refactoring if not already done
    original_valset, refactored_valset=refactor_core_code.refactor_core_code(
                valset_extens_defn=value_set_members,
                concepts=concepts,
                ) 
        # setchks_session.refactored_form=refactored_valset

# A pattern analysis of your value set indicates that you have 37 concepts that are all descendants of the concept X but there are 8 descendants that you have not in_vs.
# These m concepts (that you may have omitted in error) are: ….  Overlap (I1,E1)+overlap(I1+E2)+overlap(I1+E3) …
# Additional part (of form):
# It may help you in your further analysis to know that this list of omissions contains all the 4 descendants (and self as case may be) 
# of Y (the root of E1):            only if overlap(I1,E1) = membership(E1)

    # clauses=setchks_session.refactored_form.clause_based_rule.clauses
    clauses=refactored_valset.clause_based_rule.clauses

    include_clauses_and_memberships=[]
    exclude_clauses_and_memberships=[]
    all_excluded_concepts=set()

    ##################################################################
    # get members of clauses and separate into includes and excludes #
    # and build up total set of excludes                             #
    ##################################################################

    for clause in clauses: 
        members=ClauseMembershipAnalysis(clause=clause, concepts=concepts).members # members is a list of concept ids
        members=set(concepts[x] for x in members) # now members is a set of Concepts
        if clause.clause_type=="include":
            include_clauses_and_memberships.append((clause, members,))
        else:
            exclude_clauses_and_memberships.append((clause, members,))
            all_excluded_concepts.update(members)

    
    ###########################################
    #    output sheet header rows             #
    ###########################################
    chk_specific_sheet=ChkSpecificSheet(sheet_name="CHK10_suppl")
    setchk_results.chk_specific_sheet=chk_specific_sheet
    chk_specific_sheet.col_widths=[20,40,20,40,20,40,20]

    row=chk_specific_sheet.new_row()
    row.cell_contents=[
        "",
        "",
        "CURRENT CONTENT",
        "",
        "SUGGESTED EXTRA CONTENT",
        "",
        ]


    row=chk_specific_sheet.new_row()
    row.cell_contents=[
        "Group",
        "(Preferred Term)",
        "Concept Id",
        "Preferred Term",
        "Concept Id",
        "Preferred Term",
        "Common nature"
        ]
    #############################################
    # analyse and report on each include clause #
    #############################################

    n_SUGGESTED_NEW_MEMBERS=0
    for sorting_flag in ["ONLY_NON_ZERO", "ONLY_ZERO"]: # sorting_flag float include clauses with some 
                                                        # "interacting" exclude clauses to the top
        for i_clause, clause_and_members_tuple in enumerate(include_clauses_and_memberships):
            include_clause, include_members=clause_and_members_tuple
            members_in_vs_from_this_clause=include_members.difference(all_excluded_concepts)
            members_excluded_from_this_clause=include_members.intersection(all_excluded_concepts)
            n=len(members_excluded_from_this_clause)
            do_output_this_loop=( 
                (n==0 and sorting_flag=="ONLY_ZERO" and setchks_session.output_full_or_compact=="FULL_OUTPUT") or 
                (n>1 and sorting_flag=="ONLY_NON_ZERO") 
                )
            if do_output_this_loop:
                if sorting_flag=="ONLY_NON_ZERO":
                    n_SUGGESTED_NEW_MEMBERS+=n
                n_members_of_clause=len(include_members)
                n_members_of_clause_in_vs=len(members_in_vs_from_this_clause)
                n_members_of_clause_excluded=len(members_excluded_from_this_clause)
                include_cbc_id=str(include_clause.clause_base_concept_id)
                include_cbc_pt=concepts[include_cbc_id].pt
                plain_english_formatted_clause=plain_english_operators_fmts[include_clause.clause_operator] % include_cbc_id
                row=chk_specific_sheet.new_row()
                row.cell_contents=[
                plain_english_formatted_clause,
                include_cbc_pt,
                f"{n_members_of_clause_in_vs}/{n_members_of_clause}",
                "",
                f"{n_members_of_clause_excluded}/{n_members_of_clause}",
                ]
                
                
                
                for ei_clause, e_clause_and_members_tuple in enumerate(exclude_clauses_and_memberships):
                    exclude_clause, exclude_members=e_clause_and_members_tuple
                    members_of_include_that_this_exclude_removes=members_excluded_from_this_clause.intersection(exclude_members)
                    exclude_cbc_id=str(exclude_clause.clause_base_concept_id)
                    exclude_cbc_pt=concepts[exclude_cbc_id].pt
                    plain_english_formatted_clause=plain_english_operators_fmts[exclude_clause.clause_operator] % exclude_cbc_id
                    if members_of_include_that_this_exclude_removes != set():
                        n_removed=len(members_of_include_that_this_exclude_removes)
                        n_in_exclude=len(exclude_members)
                        for member in members_of_include_that_this_exclude_removes:
                            row=chk_specific_sheet.new_row()
                            row.cell_contents=[
                            "","","","",
                            str(member.concept_id),
                            member.pt,
                            plain_english_formatted_clause,
                            ]
                        row=chk_specific_sheet.new_row()
                        row.row_fill="grey"
                        row.row_height=2

                row=chk_specific_sheet.new_row()
                row.cell_contents=["","","","","","",""]
                row.row_fill="grey"
                row.row_height=4

                for member in members_in_vs_from_this_clause:
                    row=chk_specific_sheet.new_row()
                    row.cell_contents=[
                        "",
                        "",
                        str(member.concept_id),
                        member.pt
                    ]
                
                row=chk_specific_sheet.new_row()
                row.row_fill="grey"
                row.row_height=16


    if n_SUGGESTED_NEW_MEMBERS==0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[GREEN] This check has detected no issues."
                    ),
                outcome_code="CHK10-OUT-02",
                )
            ) 
        #</set_level_message>
    else:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[AMBER] This check has made suggestions for concepts that "
                    "you may wish to include. See 'CHK10_suppl' tab for more information"
                    ),
                outcome_code="CHK10-OUT-01",
                )
            )
        #</set_level_message>
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                    "Number of suggestions made"
                    ),
                value=f"{n_SUGGESTED_NEW_MEMBERS}",
                outcome_code="CHK10-OUT-03",
                )
            )
        #</set_level_count>
        
    