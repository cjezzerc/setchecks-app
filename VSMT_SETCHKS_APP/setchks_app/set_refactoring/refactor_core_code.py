
import time
import copy
import sys

from setchks_app.set_refactoring import valset_module
from setchks_app.set_refactoring.candidate_base_concept import CandidateBaseConcept

from setchks_app.set_refactoring.refactor_core_functions import (
    get_set_of_incl_cbcs_based_on_all_ancestors,
    purge_poor_quality_incl_cbcs,
    purge_perfect_fit_incl_cbcs_subsumed_by_another_perfect_fit_cbc,
    separate_cbcs_into_perfect_and_imperfect_fit_sets,
    insert_perfect_fits_into_refactored_query,
    trim_the_working_set,
    iterate_to_find_best_imperfect_fit_clauses_to_add,
    add_single_concept_clauses_for_unaccounted_for_concepts,
    assert_everything_now_included,
    get_set_of_excl_cbcs_based_on_all_ancestors,
    purge_poor_quality_excl_cbcs,
    purge_excl_cbcs_subsumed_by_excl_cbc,
    purge_excl_clauses_that_would_hit_valset_members,
    insert_excl_clauses_into_refactored_query,
    add_single_concept_excl_clauses_for_unaccounted_for_exclusions,
    final_clean_up,
    create_SCT_RULE,
    )

def refactor_core_code(
    clause_set_string=None,  # this is in DMWB format, e.g. '<25899002|=1234567|=987654|[-123137611|-<<345739873]'
    valset_extens_defn=None, # this is just a list of codes
                             # one (and only one) of above two must be provided
    concepts=None, 
    ):

    input_valset_name='input'
    output_valset_name='output'

    valsets=valset_module.ValsetCollection()
    valset=valset_module.Valset(
        clause_set_string=clause_set_string,
        valset_extens_defn=valset_extens_defn,
        valset_name='input')
    valsets.append(valset=valset)
    print(valset)

    valset=valsets[valsets.valset_name_to_id[input_valset_name]]

    print("Getting all members ..")
    valset_membership_analysis=valset_module.ValsetMembershipAnalysis(valset=valset, concepts=concepts, global_exclusions=valsets.global_exclusions, stub_out_interaction_matrix_calc=True, verbose=True)
    print(".. done getting all members")

    print("VALSET_INFO:",valset.valset_name, 
                        valset.valset_description, 
                        valset_membership_analysis.full_inclusion_list_n_members, 
                        valset_membership_analysis.full_exclusion_list_n_members, 
                        valset_membership_analysis.final_inclusion_list_n_members
                        )

    n_in_valset=len(valset_membership_analysis.final_inclusion_list)
    print("Valset %s contains %s members" % (valset.valset_name, n_in_valset))

    original_include_clause_strings=set()
    original_exclude_clause_strings=set()
    for clause in valset.clause_based_rule.clauses:
        if clause.clause_type=="include":
            original_include_clause_strings.add(clause.clause_base_concept_id)
        if clause.clause_type=="exclude":
            original_exclude_clause_strings.add(clause.clause_base_concept_id)

    print("At start - Original:   %3d include clauses and %3d exclude clauses" % (len(original_include_clause_strings),len(original_exclude_clause_strings)))

    full_valset_members_set      = set(copy.deepcopy(valset_membership_analysis.final_inclusion_list)) # this copy will stay fixed
    trimmed_valset_members_set   = set(copy.deepcopy(valset_membership_analysis.final_inclusion_list)) # this will be whittled down as things are accounted for
    print("Trimmed valset members initially contains %s members" % len(trimmed_valset_members_set))

    required_exclusions_set=set()
    refactored_query=[] # this will be a list of Clause objects; some will be includes and some will be excludes

    # problem_incl_id=113343008

    #
    #   NB at some stage need to think how the filtering of valsets will be applied later on
    #

    ######################
    ######################
    # PROCESS INCLUSIONS #
    ######################
    ######################

    ##################################################
    # this version does not deal with sticky clauses #
    ##################################################

    ###################################################################
    # this version does not deal with modelled (:=) inclusion clauses #
    ###################################################################

    ################################################
    # make initial catch all set of inclusion cbcs #
    ################################################

    print("Initialising inclusion all_incl_cbcs")

    all_inclusion_candidate_base_concept_ids, all_incl_cbcs=get_set_of_incl_cbcs_based_on_all_ancestors(
            trimmed_valset_members_set=trimmed_valset_members_set,
            valset_membership_analysis=valset_membership_analysis,
            concepts=concepts,
            )

    print("Initially there are %s cbcs" % len(all_incl_cbcs))

    ###############################
    # purge "poor quality" cbcs   #
    ###############################
    
    purge_poor_quality_incl_cbcs(all_incl_cbcs=all_incl_cbcs)
    
    print("After purging poor quality cbcs, %s cbs remain %s" % (len(all_incl_cbcs), [x.concept_id for x in all_incl_cbcs]))

    #########################################################################
    # purge perfect fit cbcs that are subsumed by another perfect fit cbc   #
    #########################################################################

    # 'Delete all redundant candidate ancestors with no true negative descendent ie those also subsumed by another candidate ancestor with no true negative descendent

    purge_perfect_fit_incl_cbcs_subsumed_by_another_perfect_fit_cbc(all_incl_cbcs=all_incl_cbcs)
  
    ###################################################################
    # separate remaining cbcs into perfect fit and imperfect fit sets #
    ###################################################################

    perfect_fit_incl_cbcs, imperfect_fit_incl_cbcs=separate_cbcs_into_perfect_and_imperfect_fit_sets(
        all_incl_cbcs=all_incl_cbcs)
    
    print("Provisionally accepted %s candidate base concepts that are perfect fits" % len(perfect_fit_incl_cbcs))
    print("Keeping as candidates %s candidate base concepts that are imperfect fits" % len(imperfect_fit_incl_cbcs))

    #############################################
    # insert perfect fits into refactored_query #
    #############################################

    insert_perfect_fits_into_refactored_query(
            perfect_fit_incl_cbcs=perfect_fit_incl_cbcs,
            refactored_query=refactored_query)    
    
    print("REFACTORED_QUERY has length", len(refactored_query))

    ####################################################################################
    # remove concepts that are captured by the clauses in the current refactored query #
    ####################################################################################

    trim_the_working_set(
        trimmed_valset_members_set=trimmed_valset_members_set,
        refactored_query=refactored_query,
        concepts=concepts,
        )
    
    print("Trimmed valset members now contains remaining %s members" % len(trimmed_valset_members_set))

    ################################
    # main inclusions finding loop #
    ################################

    iterate_to_find_best_imperfect_fit_clauses_to_add(   
        trimmed_valset_members_set=trimmed_valset_members_set,
        imperfect_fit_incl_cbcs=imperfect_fit_incl_cbcs,
        refactored_query=refactored_query,
        required_exclusions_set=required_exclusions_set,
        n_in_valset=n_in_valset,
        valset_membership_analysis=valset_membership_analysis,
        concepts=concepts,
        ) 

    print("REFACTORED_QUERY now has length", len(refactored_query))

    ####################################################################
    # Add unaccounted for concepts as explicit extra inclusion clauses #
    ####################################################################
    print("Adding clauses to cover residue of %s concepts remaining in trimmed list" % len(trimmed_valset_members_set))
    
    add_single_concept_clauses_for_unaccounted_for_concepts(
        trimmed_valset_members_set=trimmed_valset_members_set,
        refactored_query=refactored_query,
        concepts=concepts,    
        )
    #####################################
    # Double check if anything left out #
    #####################################
    
    assert_everything_now_included(
        refactored_query=refactored_query,
        full_valset_members_set=full_valset_members_set,
        concepts=concepts,
        )

    ######################
    ######################
    # REGROUP EXCLUSIONS #
    ######################
    ######################

    print("Now require %s exclusions" % len(required_exclusions_set))

    ################################################
    # make initial catch all set of exclusion cbcs #
    ################################################

    print("Initialising all_excl_cbcs")
    
    all_excl_cbcs=get_set_of_excl_cbcs_based_on_all_ancestors(
        required_exclusions_set=required_exclusions_set,
        all_inclusion_candidate_base_concept_ids=all_inclusion_candidate_base_concept_ids,
        full_valset_members_set=full_valset_members_set,
        concepts=concepts,
    )
    
    print("Initially there are %s exclusion cbcs" % len(all_excl_cbcs))

    ###############################
    # purge "poor quality" cbcs   #
    ###############################

    purge_poor_quality_excl_cbcs(all_excl_cbcs=all_excl_cbcs)
    
    print("After purging poor quality cbcs, %s excl_cbcs remain" % len(all_excl_cbcs))
   
    #########################################################
    # purge excl_cbcs that are subsumed by another excl_cbc #
    #########################################################
    
    purge_excl_cbcs_subsumed_by_excl_cbc(all_excl_cbcs=all_excl_cbcs)
    
    print("Now %s excl_cbcs remain" % len(all_excl_cbcs))

    ##############################################
    # Try delaying perfect fit check to here to  #
    # see if brings results closer to DMWB  
    # ! would that mean things can be removed because they are subsumed by something that is too broad (i.e. not a perfect fit)     #
    # ############################################

    ###################################################################################################
    ###################################################################################################
    #! Nomenclature here of perfect fit for exclusion clauses is tricky
    #! I think it means they do not hit any valset members
    #! An exclusion that excludes things not in the valset is still "perfect"
    #! But need to review this
    #! THat certainly seems to be the case of the way the valset_module determines the .is_perfect_fit 
    ###################################################################################################
    ###################################################################################################

    ######################################
    # see comments in definition of purge_excl_clauses_that_would_hit_valset_members
    # as unclear why it is needed everything by now should be perfect fit (in the exclusion sense)
    ######################################

    purge_excl_clauses_that_would_hit_valset_members(all_excl_cbcs=all_excl_cbcs)
    
    print("After purging imperfect fit cbcs, %s excl_cbcs remain" % len(all_excl_cbcs))

    ########################################
    # insert clauses into refactored_query #
    ########################################
    
    unaccounted_for_exclusions=insert_excl_clauses_into_refactored_query(
            all_excl_cbcs=all_excl_cbcs,
            refactored_query=refactored_query,
            required_exclusions_set=required_exclusions_set,
            full_valset_members_set=full_valset_members_set,
            concepts=concepts,
            )    
   
    ####################################################################
    # Add unaccounted for concepts as explicit extra exclusion clauses #
    ####################################################################

    add_single_concept_excl_clauses_for_unaccounted_for_exclusions(
        unaccounted_for_exclusions=unaccounted_for_exclusions,
        refactored_query=refactored_query,
        concepts=concepts,    
        )
 
    print("Before final clean up query_refactored contains %s clauses" % len(refactored_query))

    ##################
    # Final clean up #
    ##################

    refactored_query=final_clean_up(
        refactored_query=refactored_query,
        concepts=concepts,
    )

    print("After purging, refactored_query contains %s clauses" % len(refactored_query))

    for i_clause, clause in enumerate(refactored_query):
        print(i_clause, clause.clause_type, clause.clause_string)

    ##########################################################################################################
    # create new DMWB format rule                                                                            #
    # (needed for compatibility with valset_module as currently have no other way to create a Valset object) #
    ##########################################################################################################

    SCT_RULE=create_SCT_RULE(refactored_query)
    
    ########################################
    # Create Valset object and return data #
    ########################################

    refactored_valset=valset_module.Valset(
        clause_set_string=SCT_RULE, 
        metadata_column=valset.metadata_column, 
        valset_name=output_valset_name,
        )
    refactored_valset.apply_filters=False
    valsets.append(valset=refactored_valset)
    
    return valsets
   