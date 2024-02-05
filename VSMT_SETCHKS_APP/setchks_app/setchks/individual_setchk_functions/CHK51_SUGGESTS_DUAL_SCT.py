import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.set_refactoring.valset_module import ClauseMembershipAnalysis, ValsetMembershipAnalysis

from ..set_level_table_row import SetLevelTableRow

from ..chk_specific_sheet import ChkSpecificSheet


       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it can be called for all data_entry_extract_types
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    earlier_sct_version=setchks_session.sct_version
    later_sct_version=setchks_session.sct_version_b
    concepts_earlier=ConceptsDict(sct_version=earlier_sct_version.date_string)
    concepts_later=ConceptsDict(sct_version=later_sct_version.date_string)

    plain_english_operators_fmts={
    "=":"Just %s | %s |",
    "<":"All the descendants (not including itself) of %s | %s |",
    "<<":"All the descendants (plus itself) of %s | %s |",
    }
    
    ##################################################################
    ##################################################################
    ##################################################################
    # Refactor value set                                             #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    value_set_members=set()
    
    for mr in setchks_session.marshalled_rows: # marshalled_rows is built based on info from setchks_session.sct_version
                                                # which is the the earlier_sct_version
        concept_id=mr.C_Id
        if concept_id is not None:
            value_set_members.add(concept_id)
            
    # disable caching of refactored form as would have to be done differently since if running a batch of setchks in redis queue then
    # updates to setchks_session will be lost. Would have to run things like refactoring in a "pre" job
    # if setchks_session.refactored_form is None: # do refactoring if not already done
    original_valset, refactored_valset=refactor_core_code.refactor_core_code(
                valset_extens_defn=value_set_members,
                concepts=concepts_earlier,
                ) 
        # setchks_session.refactored_form=refactored_valset

    clauses=refactored_valset.clause_based_rule.clauses

    include_clauses_and_memberships=[]
    exclude_clauses_and_memberships=[]
    all_excluded_concepts_earlier=set()
    all_excluded_concepts_later=set()

    ##################################################################
    # get members of clauses and separate into includes and excludes #
    # and build up total set of excludes                             #
    ##################################################################

    for clause in clauses: 
        concept_ids_earlier=ClauseMembershipAnalysis(clause=clause, concepts=concepts_earlier).members # ".members" is a list of concept ids
        concept_ids_later=ClauseMembershipAnalysis(clause=clause, concepts=concepts_later).members # ".members" is a list of concept ids
        members_earlier=set(concepts_earlier[x] for x in concept_ids_earlier) # now members is a set of Concepts
        members_later=set(concepts_later[x] for x in concept_ids_later) # now members is a set of Concepts
        if clause.clause_type=="include":
            include_clauses_and_memberships.append((clause, members_earlier, members_later))
        else:
            exclude_clauses_and_memberships.append((clause, members_earlier, members_later))
            all_excluded_concepts_earlier.update(members_earlier)
            all_excluded_concepts_later.update(members_later)

    ###############################################################################
    # Whole value set analyses                                                    #
    # This info could be assembled in section above, so is slightly inefficient   #
    # but acts as a partial cross check to call the ValsetMembershipAnalysis code #
    ###############################################################################

    whole_vs_concept_ids_earlier=set(
        ValsetMembershipAnalysis(
            valset=refactored_valset,
            concepts=concepts_earlier
            ).final_inclusion_list)
    whole_vs_concept_ids_earlier=set(str(x) for x in whole_vs_concept_ids_earlier)
        
    assert whole_vs_concept_ids_earlier==value_set_members # belt and braces check that refactoring retained membership

    whole_vs_concept_ids_later=set(
        ValsetMembershipAnalysis(
            valset=refactored_valset,
            concepts=concepts_later
            ).final_inclusion_list)
    whole_vs_concept_ids_later=set(str(x) for x in whole_vs_concept_ids_later)
    
    whole_vs_concept_ids_in_common=whole_vs_concept_ids_earlier.intersection(whole_vs_concept_ids_later)
    whole_vs_concept_ids_only_in_earlier=whole_vs_concept_ids_earlier.difference(whole_vs_concept_ids_later)
    whole_vs_concept_ids_only_in_later=whole_vs_concept_ids_later.difference(whole_vs_concept_ids_earlier)

    ###########################################
    #    output sheet header rows             #
    ###########################################
    chk_specific_sheet=ChkSpecificSheet(sheet_name="CHK51_suppl")
    setchk_results.chk_specific_sheet=chk_specific_sheet
    # chk_specific_sheet.col_widths=[20,40,20,40,20,40,20,40]
    chk_specific_sheet.col_widths=[60,20,40,20,40,20,40]

    row=chk_specific_sheet.new_row()
    row.cell_contents=[
        "",
        "",
        "Only in earlier",
        "",
        "Common to both",
        "",
        "Only in later",
        "",
        ]


    row=chk_specific_sheet.new_row()
    row.cell_contents=[
        "Group",
        "Concept Id",
        "Preferred Term",
        "Concept Id",
        "Preferred Term",
        "Concept Id",
        "Preferred Term",
        ]
    #############################################
    # analyse and report on each include clause #
    #############################################

    for sorting_flag in ["ONLY_NON_ZERO", "ONLY_ZERO"]: # sorting_flag float include clauses with something in earlier
                                                        # or later column to top as those are most interesting
        for i_clause, clause_and_members_tuple in enumerate(include_clauses_and_memberships):
            include_clause, include_members_earlier, include_members_later=clause_and_members_tuple
            members_in_vs_from_this_clause_earlier=include_members_earlier.difference(all_excluded_concepts_earlier)
            members_in_vs_from_this_clause_later=include_members_later.difference(all_excluded_concepts_later)
            
            # as the "member" object for a particular concept_id will be different between the two releases
            # now need to build dict of members keyed by concept_id and sets of concept_ids so that 
            # can do appropriate intersections on concept_ids and then rebuild the sets of members
            # (at least this is one way to code it..!)
            
            # build the dicts of members and sets of concept_ids:
            members_in_vs_from_this_clause_earlier_dict={ m.concept_id:m for m in members_in_vs_from_this_clause_earlier}
            concept_ids_in_vs_from_this_clause_earlier=set(members_in_vs_from_this_clause_earlier_dict.keys())
            members_in_vs_from_this_clause_later_dict={ m.concept_id:m for m in members_in_vs_from_this_clause_later}
            concept_ids_in_vs_from_this_clause_later=set(members_in_vs_from_this_clause_later_dict.keys())

            # now do set operations on concept_id sets
            concept_ids_in_vs_from_this_clause_common=concept_ids_in_vs_from_this_clause_earlier.intersection(
                                                                            concept_ids_in_vs_from_this_clause_later)
            concept_ids_in_vs_from_this_clause_only_earlier=concept_ids_in_vs_from_this_clause_earlier.difference(
                                                                            concept_ids_in_vs_from_this_clause_later)
            concept_ids_in_vs_from_this_clause_only_later=concept_ids_in_vs_from_this_clause_later.difference(
                                                                            concept_ids_in_vs_from_this_clause_earlier)

            # now build member sets back from member dicts and concept_id sets
            members_in_vs_from_this_clause_common=set(members_in_vs_from_this_clause_earlier_dict[cid] 
                                                        for cid in concept_ids_in_vs_from_this_clause_common)
            members_in_vs_from_this_clause_only_earlier=set(members_in_vs_from_this_clause_earlier_dict[cid] 
                                                        for cid in concept_ids_in_vs_from_this_clause_only_earlier)
            members_in_vs_from_this_clause_only_later=set(members_in_vs_from_this_clause_later_dict[cid] 
                                                        for cid in concept_ids_in_vs_from_this_clause_only_later)
            
            # members_excluded_from_this_clause=include_members.intersection(all_excluded_concepts)
            # n_members_of_clause=len(include_members)
            n_members_of_clause_in_vs_common=len(members_in_vs_from_this_clause_common)
            n_members_of_clause_in_vs_only_earlier=len(members_in_vs_from_this_clause_only_earlier)
            n_members_of_clause_in_vs_only_later=len(members_in_vs_from_this_clause_only_later)
            # n_members_of_clause_excluded=len(members_excluded_from_this_clause)

            # print("1:",members_in_vs_from_this_clause_only_earlier,members_in_vs_from_this_clause_common,members_in_vs_from_this_clause_only_later)
            n=n_members_of_clause_in_vs_only_earlier+n_members_of_clause_in_vs_only_later
            do_output_this_loop=( 
                (n==0 and sorting_flag=="ONLY_ZERO" and setchks_session.output_full_or_compact=="FULL_OUTPUT") or 
                (n>0 and sorting_flag=="ONLY_NON_ZERO") 
                )
            if do_output_this_loop:
                include_cbc_id=str(include_clause.clause_base_concept_id)
                include_cbc_pt=concepts_earlier[include_cbc_id].pt
                # plain_english_formatted_clause=plain_english_operators_fmts[include_clause.clause_operator] % include_cbc_id
                plain_english_formatted_clause=(
                    plain_english_operators_fmts[include_clause.clause_operator] % 
                    (include_cbc_id, include_cbc_pt)
                    )
                row=chk_specific_sheet.new_row()
                row.cell_contents=[
                plain_english_formatted_clause,
                # include_cbc_pt,
                f"{n_members_of_clause_in_vs_only_earlier}",
                "", 
                f"{n_members_of_clause_in_vs_common}",
                "",
                f"{n_members_of_clause_in_vs_only_later}", 
                ]
                
                for member in members_in_vs_from_this_clause_only_later:
                    row=chk_specific_sheet.new_row()
                    row.cell_contents=[
                        "","","","","",
                        str(member.concept_id),
                        member.pt,
                    ]
                
                # row=chk_specific_sheet.new_row()
                # row.cell_contents=["","","","","","",""]
                # row.row_fill="grey"
                # row.row_height=4
                
                for member in members_in_vs_from_this_clause_only_earlier:
                    row=chk_specific_sheet.new_row()
                    row.cell_contents=[
                        "",
                        str(member.concept_id),
                        member.pt,
                    ]
                
                # row=chk_specific_sheet.new_row()
                # row.cell_contents=["","","","","","",""]
                # row.row_fill="grey"
                # row.row_height=4

                for member in members_in_vs_from_this_clause_common:
                    row=chk_specific_sheet.new_row()
                    row.cell_contents=[
                        "","","",
                        str(member.concept_id),
                        member.pt,
                    ]
                
                row.is_end_of_clause=True
                # row=chk_specific_sheet.new_row()
                # row.row_fill="grey"
                # row.row_height=16

    if (len(whole_vs_concept_ids_only_in_earlier) + len (whole_vs_concept_ids_only_in_later))==0:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[GREEN] This check has detected no issues."
                    ),
                outcome_code="CHK51-OUT-01",
                )
            ) 
        #</set_level_message>
    else:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[AMBER] This check has made suggestions for Concepts that "
                    "you may wish to add or remove from the value set due to the change in content of the release."
                    "See 'CHK51_suppl' tab for suggestions."
                    ),
                outcome_code="CHK51-OUT-04",
                )
            )
        #</set_level_message>
        
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                "Number of suggestions for Concepts to consider for removal from the value set"
                    ),
                value=f"{len(whole_vs_concept_ids_only_in_earlier)}",
                outcome_code="CHK51-OUT-02",
                )
            )
        #</set_level_count>
        
        #<set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=(
                "Number of suggestions for Concepts to consider for addition to the value set"
                    ),
                value=f"{len(whole_vs_concept_ids_only_in_later)}",
                outcome_code="CHK51-OUT-03",
                )
            )
        #</set_level_count>
    # import pdb; pdb.set_trace()