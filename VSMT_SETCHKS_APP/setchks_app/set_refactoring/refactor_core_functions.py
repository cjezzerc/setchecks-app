""" the core functions involved in refactoring """

import time, sys

from setchks_app.set_refactoring.candidate_base_concept import CandidateBaseConcept
from setchks_app.set_refactoring.valset_module import Clause
from setchks_app.set_refactoring.valset_module import ClauseMembershipAnalysis

##########################################
# get_set_of_cbcs_based_on_all_ancestors #
##########################################

def get_set_of_incl_cbcs_based_on_all_ancestors(
    trimmed_valset_members_set=None,
    valset_membership_analysis=None,
    concepts=None,
    ):
    start_timea=time.time()
    all_inclusion_candidate_base_concept_ids=set()
    for concept_id in trimmed_valset_members_set:
        all_inclusion_candidate_base_concept_ids.update(concepts[concept_id].ancestors)
    # print("Initially:",all_candidate_base_concept_ids)
    print("Step1 took (in seconds)", time.time()-start_timea)    

    # remove root snomedct concept
    print(138875005 in all_inclusion_candidate_base_concept_ids)
    print(len(all_inclusion_candidate_base_concept_ids))
    print(all_inclusion_candidate_base_concept_ids)
    all_inclusion_candidate_base_concept_ids.discard(138875005)
    print(len(all_inclusion_candidate_base_concept_ids))

    start_timeb=time.time()
    all_incl_cbcs=set()
    for i_cbc, concept_id in enumerate(all_inclusion_candidate_base_concept_ids):
        print("Getting cbc %s ( %s of %s )" % ( concept_id, i_cbc, len(all_inclusion_candidate_base_concept_ids)))
        cbc=CandidateBaseConcept(concept_id=concept_id, concepts=concepts, target_members=valset_membership_analysis.final_inclusion_list)
        all_incl_cbcs.add(cbc)
    print("Step2 took (in seconds)", time.time()-start_timeb)   
    return all_inclusion_candidate_base_concept_ids, all_incl_cbcs 

################################
# purge_poor_quality_incl_cbcs #
################################

def purge_poor_quality_incl_cbcs(all_incl_cbcs=None):
    to_be_purged_set=set()
    for cbc in all_incl_cbcs:
        # print(cbc)
        to_be_purged_reason=""
        if cbc.n_desc_plus_self_in_membership<2:
            to_be_purged_reason+="reason1 "
        if (cbc.n_desc_plus_self_not_in_membership==1) and (cbc.is_in_membership is False) and (cbc.n_children_all==1):
            to_be_purged_reason+="reason2 "
        if (float(cbc.n_children_in_membership)/cbc.n_children_all)<0.5:
            to_be_purged_reason+="reason3 "
        if ((float(cbc.n_children_in_membership)/cbc.n_children_all)<0.6) and (cbc.n_children_all>9):
            to_be_purged_reason+="reason4 "
        if to_be_purged_reason != "":
            # if cbc.concept_id==problem_incl_id:
            #     print("PURGING %s reason: %s" % (problem_incl_id, to_be_purged_reason))
            # print("PURGED-REASON:", to_be_purged_reason)
            to_be_purged_set.add(cbc)
        else:
            # if cbc.concept_id==problem_incl_id:
            #     print("NOT PURGING %s : n_in_memb %s | is_perfect_fit %s | n_all %s " % (problem_incl_id, cbc.n_desc_plus_self_in_membership, cbc.is_perfect_fit, cbc.n_desc_plus_self_all))
            pass
            # print("NOT_PURGED")
        # print(to_be_purged_reason)
        # print("========================")
    all_incl_cbcs.difference_update(to_be_purged_set)


##############################################################
# purge_perfect_fit_incl_cbcs_subsumed_by_another_perfect_fit_cbc #
##############################################################

def purge_perfect_fit_incl_cbcs_subsumed_by_another_perfect_fit_cbc(all_incl_cbcs=None):
    print("Entering reconstructed (less) time consuming loop")
    start_time2=time.time()
    to_be_purged_set=set()
    concepts_ids={cbc.concept_id for cbc in all_incl_cbcs if cbc.is_perfect_fit}
    for cbc in all_incl_cbcs:
        if cbc.is_perfect_fit and (cbc.concept.ancestors.isdisjoint(concepts_ids) is False):
            to_be_purged_set.add(cbc)
    print("Purging %s candidate base concepts that are perfectly subsumed by an ancestor" % len(to_be_purged_set))
    t2=time.time()-start_time2
    print("Purging redundant prefect fit clauses took (in seconds)", time.time()-start_time2)    

    all_incl_cbcs.difference_update(to_be_purged_set)
    print("That took (in seconds)", time.time()-start_time2)

##############################################################
# separate_cbcs_into_perfect_and_imperfect_fit_sets          #
##############################################################

def separate_cbcs_into_perfect_and_imperfect_fit_sets(all_incl_cbcs=None):
    perfect_fit_incl_cbcs = { cbc for cbc in all_incl_cbcs if cbc.is_perfect_fit==True }
    imperfect_fit_incl_cbcs = all_incl_cbcs.difference(perfect_fit_incl_cbcs)
    return perfect_fit_incl_cbcs, imperfect_fit_incl_cbcs

######################################################
# insert_perfect_fits_into_refactored_query          #
######################################################

def insert_perfect_fits_into_refactored_query(
    perfect_fit_incl_cbcs=None,
    refactored_query=None):
    for cbc in perfect_fit_incl_cbcs:
        clause_string=cbc.operator+str(cbc.concept_id)
        clause=Clause(clause_string)
        refactored_query.append(clause)


#################################
# trim the working set          #
#################################

def trim_the_working_set(
    trimmed_valset_members_set=None,
    refactored_query=None,
    concepts=None,
    ):
    concepts_captured_by_refactored_query=set()
    for clause in refactored_query:
        concepts_captured_by_clause=ClauseMembershipAnalysis(clause=clause, concepts=concepts).members
        concepts_captured_by_refactored_query.update(concepts_captured_by_clause)
    n_members_captured_by_concepts=len(trimmed_valset_members_set.intersection(concepts_captured_by_refactored_query))
    trimmed_valset_members_set.difference_update(concepts_captured_by_refactored_query)
    print("Refactored query captures %s members" % n_members_captured_by_concepts)

#####################################################
# iterate_to_find_best_imperfect_fit_clauses_to_add #
#####################################################

def iterate_to_find_best_imperfect_fit_clauses_to_add(   
    trimmed_valset_members_set=None,
    imperfect_fit_incl_cbcs=None,
    refactored_query=None,
    required_exclusions_set=None,
    n_in_valset=None,
    valset_membership_analysis=None,
    concepts=None,
    ):    
    ideal_clause_count=1
    max_clause_count=300
    min_fit_threshold=0.5

    fit_threshold=0.9
    zoom=ideal_clause_count
    terminate_condition_reached=False
    winner_exists_at_current_zoom=False
    winner_cbc=None
    n_clauses_added=0

    iteration=0

    if len(trimmed_valset_members_set)==0: # this is a specific line in DMWB code; not sure completely in line with logic of some of the comment about
                                            # needing to still consider imperfect fit clauses even if all are covered by perfect fit. But that comment may have be superseded by later thoughts.
        terminate_condition_reached=True

    while not terminate_condition_reached:
        iteration+=1
        list_size=len(trimmed_valset_members_set)
        print("\n\nIteration %s :  LSize=%s Fit=%s Z=%s" % (iteration, list_size, fit_threshold, zoom))

        scores=[]
        #Update scores of all remaining cbcs
        for cbc in imperfect_fit_incl_cbcs:
            cbc.set_score(zoom=zoom, verbose=False)
            scores.append((cbc.score, cbc))
            # if cbc.concept_id==problem_incl_id:
            #     print("PROBLEM_INCL SCORE %s %s" % (problem_incl_id, cbc.score))

        #Find the cbc with highest score
        cbcs_sorted_by_score=sorted(imperfect_fit_incl_cbcs, key= lambda cbc: cbc.score, reverse=True)
        if len(cbcs_sorted_by_score)>0:
            cbcs_list_not_empty=True
            winner_cbc=cbcs_sorted_by_score[0]
            winner_base_concept=concepts[winner_cbc.concept_id]
        else:
            cbcs_list_not_empty=False  # still carry on as that is what DMWB does

        if cbcs_list_not_empty and winner_cbc.score >= fit_threshold-0.001: # 0.001 is to allow for rounding error; on first pass 0.899999999999 can occur
            winner_exists_at_current_zoom=True
            print("Winner is %s with score %s" % (winner_base_concept.concept_id, winner_cbc.score))
            if len(cbcs_sorted_by_score)>1:
                print("Secondplace is %s with score %s" % (cbcs_sorted_by_score[1].concept_id , cbcs_sorted_by_score[1].score))
            else:
                print("Secondplace: there are no more cbcs in list")
            #Add new clause based on winner to refactored_query and find what concepts it captures
            clause=Clause(winner_cbc.clause_string)
            print(winner_cbc.clause_string)
            refactored_query.append(clause)
            n_clauses_added+=1
            concepts_captured_by_clause=ClauseMembershipAnalysis(clause=clause, concepts=concepts).members
            
            #Remove these captured concepts from the trimmed list
            n_records_to_be_removed_from_trimmed_set=len(trimmed_valset_members_set.intersection(concepts_captured_by_clause))
            trimmed_valset_members_set.difference_update(concepts_captured_by_clause)

            #Add to the required exclusions set any captured concepts that are not in the valset 
            concepts_captured_that_will_need_exclusion=set(concepts_captured_by_clause).difference(set(valset_membership_analysis.final_inclusion_list))
            required_exclusions_set.update(concepts_captured_that_will_need_exclusion)

            #Get rid of winner and its descendants from cbcs
            to_be_purged_set=set()
            for cbc in imperfect_fit_incl_cbcs:
                if cbc.concept_id in winner_base_concept.descendants or cbc==winner_cbc:
                    to_be_purged_set.add(cbc)
            imperfect_fit_incl_cbcs.difference_update(to_be_purged_set)
            print("Purged %s cbcs as descendants of winner or the winner itself" % len(to_be_purged_set))
            
            #Look to see if although found a winner things are being found in clauses that are too small (not convinced by logic here)
            fold_left=float(n_in_valset)/(n_records_to_be_removed_from_trimmed_set+1) # I am not convinced by this section ? intended definition of ClauseCoverage in original code
            if fold_left>1000:
                new_fit_threshold=round(fit_threshold*0.9,3)
                if (new_fit_threshold>min_fit_threshold) and (new_fit_threshold<fit_threshold):
                    print("Winning clause too small (%s of remaining records covered removed) - detuning" % n_records_to_be_removed_from_trimmed_set)
                    fit_threshold = new_fit_threshold
                    zoom = ideal_clause_count
        else:
            # 'If no winner was found on this pass, then try to (de)tune the score weighting function
            # 'so that smaller and/or less well fitting clauses are allowed:
            if (zoom <= max_clause_count) and (zoom <= list_size) and (zoom != round((zoom * 1.1) + 0.5, 0)):
            #   'Initially, simply increment the Zoom (as long as it hasn't hit the MaxClauseCount buffer)
            #   'This shifts the weighting function toward favouring smaller clusters that might have Fit above the current
            #   'threshold but that currently score lower than some larger cluster but with sub-threshold Fit
                zoom = round((zoom * 1.1) + 0.5, 0)
            else:
            #   'Zoom has already hit the buffers (ie we're already considering the smallest clusters we're interested in getting)
                if not (winner_exists_at_current_zoom):
                    # 'If no winner has been found in any pass at ANY Zoom level and with the prevailing FitThreshold
                    # 'then propose a revised FitThreshold that's just low enough to allow the currently highest scoring clause to pass through
                        if winner_cbc:
                            new_fit_threshold = winner_cbc.score
                        else:
                            #this is where there never has been ANY winner (e.g. enters loop with empty set of cbcs)
                            new_fit_threshold=-999 # this will casue termination of loop
                        print("INCLUSION FIT THRESHOLD VALUE RECALIBRATION")
                else:
                    # 'If a winner HAS previously been found at SOME zoom level and with the prevailing FitThreshold
                    # 'then propose a less drastically lowered FitThreshold
                    new_fit_threshold = round((fit_threshold * 0.9), 3)
                if (new_fit_threshold > min_fit_threshold) and (new_fit_threshold < fit_threshold):
                    # 'As long as the proposed new FitThreshold is above some minimum floor Fit level
                    # '(and also as long as its actually different from the current FitThreshold...)
                    # 'then accept it, and reset the Zoom to the normal starting level for each pass
                    # fit_threshold = new_fit_threshold
                    fit_threshold=round(new_fit_threshold*0.95,3) # added 25oct23 after discussion with Jeremy Rogers
                                                                 # JR added this to DMWB due to a small rounding issue
                                                                 # that stopped the python code and DMWB getting same results
                                                                 # in a few cases
                    zoom = ideal_clause_count
                    winner_exists_at_current_zoom=False
                else:
                    # 'Otherwise we've hit the buffers: the weighting function can't be (de)tuned any further
                    print("TERMINATING: Can't detune inclusion weighting function any further")
                    print("Next best fitting candidate has score of ", new_fit_threshold)
                    print("Minimum fit threshold is ", min_fit_threshold)
                    terminate_condition_reached = True
    print("\nIn loop added %s extra clauses" % n_clauses_added)

###########################################################
# add_single_concept_clauses_for_unaccounted_for_concepts #
###########################################################

def add_single_concept_clauses_for_unaccounted_for_concepts(
    trimmed_valset_members_set=None,
    refactored_query=None,
    concepts=None,    
    ):
    for concept_id in trimmed_valset_members_set:
        if concepts[concept_id].descendants==set():
            operator="<<" # if no descendants use "<<" so that if descendants added they will be included by default
        else:
            operator="=" # else have decendants so use "=" so do not include non members
        clause_string=operator+str(concept_id)
        print("Adding clause", clause_string)
        refactored_query.append(Clause(clause_string))

##################################
# assert_everything_now_included #
##################################

def assert_everything_now_included(
    refactored_query=None,
    full_valset_members_set=None,
    concepts=None,
    ):
    total_inclusions=set()
    for clause in refactored_query:
        total_inclusions.update(set(ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))
    unaccounted_for=full_valset_members_set.difference(total_inclusions)
    inclusion_check=unaccounted_for==set()
    print("INCLUSION_CHECK:", inclusion_check)
    if not inclusion_check:
        print("ERROR: Exiting as refactored_query does not account for everything")
        sys.exit()

###############################################
# get_set_of_excl_cbcs_based_on_all_ancestors # ca. lines 978-1002
###############################################

def get_set_of_excl_cbcs_based_on_all_ancestors(
        required_exclusions_set=None,
        all_inclusion_candidate_base_concept_ids=None,
        full_valset_members_set=None,
        concepts=None,
    ):
    
    all_exclusion_candidate_base_concept_ids=set()

    for concept_id in required_exclusions_set:
        all_exclusion_candidate_base_concept_ids.update(concepts[concept_id].ancestors)

    # print("PROBLEM_ID: Is %s in required_exclusions_set? %s" % (problem_id, problem_id in all_exclusion_candidate_base_concept_ids))

    print("Collated list of %s cbcs in all_exclusion_candidate_base_concept_ids" % len(all_exclusion_candidate_base_concept_ids))
    print(all_exclusion_candidate_base_concept_ids)
    #remove concepts that are also in ancestors lists of valset members ca. DMWB999
    n_to_remove=len(all_exclusion_candidate_base_concept_ids.intersection(all_inclusion_candidate_base_concept_ids))
    print("Discarding %s cbcs because also an inclusion ancestor" % n_to_remove)
    all_exclusion_candidate_base_concept_ids.difference_update(all_inclusion_candidate_base_concept_ids)
    print("Now have list of %s cbcs in all_exclusion_candidate_base_concept_ids" % len(all_exclusion_candidate_base_concept_ids))
    # print("PROBLEM_ID: Is %s STILL1 in required_exclusions_set? %s" % (problem_id, problem_id in all_exclusion_candidate_base_concept_ids))


    #Now build the all_excl_cbcs
    all_excl_cbcs=set()
    for concept_id in all_exclusion_candidate_base_concept_ids:
        #NOT SURE ABOUT MUST_AVOID_SET logic
        cbc=CandidateBaseConcept(concept_id=concept_id, concepts=concepts, target_members=required_exclusions_set, must_avoid_set=full_valset_members_set)
        all_excl_cbcs.add(cbc)
        # print(cbc)

    return all_excl_cbcs

################################
# purge_poor_quality_excl_cbcs #
################################

def purge_poor_quality_excl_cbcs(all_excl_cbcs=None):
    to_be_purged_set=set()
    for cbc in all_excl_cbcs:
        to_be_purged_reason=""
        # DMWB:Ignore candidate groupers if the number of true members of the exclusion set subsumed by it is below the threshold
        if cbc.n_desc_plus_self_in_membership<2: #line DMWB1035 
            to_be_purged_reason+="reason1 "

        # this chunk for some reason moved later; see below; remove this bit when understand why
        # in fact if look at chunk below not sure why this was ever in the code at all
        # if (not cbc.is_perfect_fit):
        #     to_be_purged_reason+="reason2 "


        # if (float(cbc.n_desc_plus_self_in_membership)/cbc.n_desc_plus_self_all)<0.5:
        if (cbc.n_desc_plus_self_all - cbc.n_desc_plus_self_in_membership) > cbc.n_desc_plus_self_in_membership: # (line DMWB1040)
            to_be_purged_reason+="reason3 "
        # TempDB.Execute "DELETE FROM greedy_ancestors_x WHERE TRUENEG = 1 AND INCLUDE = FALSE AND ALLCHILDREN = 1;" 
        if (cbc.n_desc_plus_self_not_in_membership==1 and cbc.is_in_membership==True and cbc.n_children_all==1): # line DMWB1037
            to_be_purged_reason+="reason4 "
        if to_be_purged_reason != "":
            # print("PURGED-REASON:", to_be_purged_reason)
            to_be_purged_set.add(cbc)
       
    all_excl_cbcs.difference_update(to_be_purged_set)


########################################
# purge_excl_cbcs_subsumed_by_excl_cbc # Lines DMWB1042-1044
########################################

def purge_excl_cbcs_subsumed_by_excl_cbc(all_excl_cbcs=None):
    print("Entering time consuming loop")
    start_time3=time.time()
    to_be_purged_set=set()
    for cbc1 in all_excl_cbcs:
        if cbc1.n_desc_plus_self_not_in_membership==0: #"b.TRUENEG=0"
            for cbc2 in all_excl_cbcs:
                if cbc2.n_desc_plus_self_not_in_membership==0: #"a.TRUENEG=0"
                    if cbc1!=cbc2 and (cbc2.concept_id in cbc1.concept.descendants):
                        to_be_purged_set.add(cbc2)
    print("Purging %s excl_cbcs that are perfectly subsumed by an ancestor" % len(to_be_purged_set))

    all_excl_cbcs.difference_update(to_be_purged_set)
    
    print("That purge took (in seconds)", time.time()-start_time3)



####################################################
# purge_excl_clauses_that_would_hit_valset_members #
####################################################

def purge_excl_clauses_that_would_hit_valset_members(all_excl_cbcs=None):
    to_be_purged_set=set()
    for cbc in all_excl_cbcs:
        to_be_purged_reason=""
        assert(cbc.is_perfect_fit) # This whole function should I think never find anything that hits a valset member because 
                                    # See comment above: #remove concepts that are also in ancestors lists of valset members ca. DMWB999
                                    # I am not sure why this function exists
        if (not cbc.is_perfect_fit):
            to_be_purged_reason+="reason2 "
            # print("PURGED-REASON:", to_be_purged_reason)
            to_be_purged_set.add(cbc)

    all_excl_cbcs.difference_update(to_be_purged_set)

##############################################
# insert_excl_clauses_into_refactored_query  #
##############################################

def insert_excl_clauses_into_refactored_query(
            all_excl_cbcs=None,
            refactored_query=None,
            required_exclusions_set=None,
            full_valset_members_set=None,
            concepts=None,
            ):    
    total_exclusions=set()
    for cbc in all_excl_cbcs:
        print(cbc.clause_string, cbc.concept.pt, cbc.n_desc_plus_self_in_membership ,"of", cbc.n_desc_plus_self_all)
        clause=Clause("-"+cbc.clause_string)
        refactored_query.append(clause)
        total_exclusions.update(set(ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))
    unaccounted_for_exclusions=required_exclusions_set.difference(total_exclusions) 
    valset_members_hit=full_valset_members_set.intersection(total_exclusions)
    print("VALSET hit: ", len(valset_members_hit))
    return unaccounted_for_exclusions

###################################################################
# add_single_concept_excl_clauses_for_unaccounted_for_exclusions  #
###################################################################

def add_single_concept_excl_clauses_for_unaccounted_for_exclusions(
    unaccounted_for_exclusions=None,
    refactored_query=None,
    concepts=None,    
    ):
    print("Adding clauses to cover residue of %s concepts remaining in unaccounted_for_exclusions" % len(unaccounted_for_exclusions))
    for concept_id in unaccounted_for_exclusions:
        if concepts[concept_id].descendants==set():
            operator="<<" # if no descendants use "<<" so that if descendants added they will be included by default
        else:
            operator="=" # else have decendants so use "=" so do not include non members
        clause_string="-"+operator+str(concept_id)
        print("Adding clause", clause_string)
        refactored_query.append(Clause(clause_string))


###################
# final_clean_up  #
###################

def final_clean_up(
    refactored_query=None,
    concepts=None,
    ):
    start_time_clean_up=time.time()

    to_be_purged_set=set()

    clause_members_sets=[]
    for i_clause, clause in enumerate(refactored_query):
        clause_members_sets.append(set(ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))

    for i_clause2, clause2 in enumerate(refactored_query):
        purge2=False
        to_be_purged_reason=""
        for i_clause1, clause1 in enumerate(refactored_query):
            if clause1.clause_base_concept_id in concepts: 
                if (i_clause1 != i_clause2) and (clause1.clause_type==clause2.clause_type): # NB in DMWB INCLUDE meanes include/exclude for a cluase; but for a (base) concept it means is the concept 
                                                                                            # in the valset (I think)
                    if (i_clause2>i_clause1) and (clause1.clause_string==clause2.clause_string): # check for duplicate
                        purge2=True
                        to_be_purged_reason+="DUPLICATE "
                    if (clause1.clause_base_concept_id==clause2.clause_base_concept_id):
                        # remove < clauses on a concept if a << clause exists on the same concept;  
                        if (clause2.clause_operator == "<") and (clause1.clause_operator == "<<"): 
                            purge2=True
                            to_be_purged_reason+="<_WHERE_<<_EXISTS "
                        # remove any = clause made redundant by a << on the same concept; 
                        if (clause2.clause_operator == "=") and (clause1.clause_operator == "<<"): 
                            purge2=True
                            to_be_purged_reason+="=_WHERE_<<_EXISTS "
                    # remove clauses that are subsumed by another clause with << or < extension;
                    # if clause_members_sets[i_clause2] < clause_members_sets[i_clause1]: # this definition retired sep22 in favour of JR's defn of subsumed here based on descendancy
                                        
                    if (clause1.clause_operator in ["<","<<"]) and (clause2.clause_base_concept_id in concepts[clause1.clause_base_concept_id].descendants): 
                        purge2=True
                        to_be_purged_reason+="SUBSUMED_BY_%s " % i_clause1 
                
        if purge2:
            print(i_clause2, clause2.clause_type, clause2.clause_string,"will be purged. Reason:", to_be_purged_reason)
            to_be_purged_set.add(clause2)
        else:
            # print(i_clause2,"Not purged")
            print(i_clause2, clause2.clause_type, clause2.clause_string,"Not purged")

    print(f"To be purged set: {to_be_purged_set}")
    purged_refactored_query=[]
    for clause in refactored_query:
        print(clause.clause_string, clause in to_be_purged_set)
        if clause not in to_be_purged_set:
            purged_refactored_query.append(clause)
    refactored_query=purged_refactored_query
    return refactored_query

    #####
    # Globex things (DMWB1130-1136) not implemented yet
    # These would delete concept only clauses if base concept in GLOBEX
    # And would convert << to < likewise
    #####
    print("Globex pruning not implemented yet")

    print("CLEAN_UP: took (in seconds)", time.time()-start_time_clean_up)

###################
# create_SCT_RULE #
###################

def create_SCT_RULE(refactored_query):
    include_SCT_RULE=""
    exclude_SCT_RULE=""
    for clause in refactored_query:

        if clause.clause_type=="include":
            include_SCT_RULE+= clause.clause_string + "|"
        elif clause.clause_type=="exclude":
            exclude_SCT_RULE+=  "-" + clause.clause_string + "|"
        else:
            print("ERROR, exiting:invalid clause_type: %s" % clause.clause_type)
            sys.exit()
    if exclude_SCT_RULE:
        SCT_RULE= include_SCT_RULE + "[" + exclude_SCT_RULE
    else:
        SCT_RULE= include_SCT_RULE
    print(SCT_RULE)
    return SCT_RULE
