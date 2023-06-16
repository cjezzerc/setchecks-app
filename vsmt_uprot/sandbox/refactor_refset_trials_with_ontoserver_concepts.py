#!/usr/bin/env python

import os
import os.path
import sys
import time
import pickle
import copy

import refset_module_modified
# import msaccess
# import release_processing

sys.path.remove('/cygdrive/c/Users/jeremy/GIT/snomed_python')

sys.path.append("/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/vsmt_uprot/")

import terminology_server_module
from concept_module import ConceptsDict


class CandidateBaseConcept():
    def __init__(self, concept_id=None, concepts=None, target_members=None, must_avoid_set=None):
        self.concept_id=concept_id
        self.concept=concepts[concept_id]
        self.concepts=concepts
        # self.refset_membership_analysis=refset_membership_analysis
        self.target_members=target_members
        self.score=-999


        # avoid this:    self.desc_plus_self=copy.deepcopy(self.concept.descendants)
        # takes ages for root concept etc
        self.is_in_membership                   = concept_id in self.target_members

        self.n_desc_plus_self_all               = len(self.concept.descendants)+1  # this seems in line with definition of NUMDESCENDENTS
        self.n_desc_plus_self_in_membership     = len(self.concept.descendants.intersection(self.target_members)) 
        if self.is_in_membership:
            self.n_desc_plus_self_in_membership+=1 # this seems lin line with definition of TRUEPOS
        self.n_desc_plus_self_not_in_membership = self.n_desc_plus_self_all-self.n_desc_plus_self_in_membership # this seesm in line wiht definitions of TRUENEG 

        if must_avoid_set is not None:
            self.refset_members_hit=self.concept.descendants.intersection(must_avoid_set)
            # print(len(must_avoid_set))

        if self.is_in_membership:
            self.operator="<<"
        else:
            self.operator="<"
        
        if must_avoid_set is not None:
            self.is_perfect_fit = self.concept.descendants.isdisjoint(must_avoid_set)
        else:
            if self.is_in_membership:
                self.is_perfect_fit                 = self.n_desc_plus_self_not_in_membership==0
            else:
                self.is_perfect_fit                 = self.n_desc_plus_self_not_in_membership==1 # with "<" operator self will be ignored

        self.clause_string=self.operator+str(self.concept_id)

        self.n_children_all                     = len(self.concept.children)
        self.n_children_in_membership           = len(set(self.concept.children).intersection(self.target_members))

    def __str__(self):
        str_str="\nCandidateBaseConcept:\n-------------\n"
        str_str+="concept_id: %s\n" % self.concept_id
        str_str+="fsn: %s\n" % self.concepts[self.concept_id].fsn
        str_str+="is_in_membership: %s\n" % self.is_in_membership
        str_str+="is_perfect_fit: %s\n" % self.is_perfect_fit
        str_str+="clause_string: %s\n" % self.clause_string
        str_str+="n_desc_plus_self_all: %s\n" % self.n_desc_plus_self_all
        str_str+="n_desc_plus_self_in_membership: %s\n" % self.n_desc_plus_self_in_membership
        str_str+="n_desc_plus_self_not_in_membership: %s\n" % self.n_desc_plus_self_not_in_membership
        str_str+="n_children_all: %s\n" % self.n_children_all
        str_str+="n_children_in_membership: %s\n" % self.n_children_in_membership
        # str_str+="refset_members_hit: %s\n" % self.refset_members_hit
        return str_str

    def set_score(self, *, zoom=None, verbose=False ):
        self.score=self.n_desc_plus_self_in_membership/self.n_desc_plus_self_all
        if not self.is_in_membership:
            self.score=self.score*0.95
        if self.score<0.7:
            if verbose:
                print(float(len(self.target_members)), self.n_desc_plus_self_in_membership, float(len(self.target_members))/self.n_desc_plus_self_in_membership )

            self.score=self.score*(1.0/(abs((float(len(self.target_members))/self.n_desc_plus_self_in_membership)-zoom)+1))

#   ##############################
#   # Load SNOMED-CT from pickle #
#   ##############################

# branch_tag="UKCL_v34.1_03aug22"
# pickle_filename_prefix="RELN_IDS_"
# concepts=release_processing.read_concepts_pickle_file(branch_tag=branch_tag, pickle_filename_prefix=pickle_filename_prefix, verbose=True)

# set up to access concepts from terminology server rather than pickle file

# terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
terminology_server=terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                    auth_url=os.environ["ONTOAUTH_INSTANCE"])
# concepts=ConceptsDict(terminology_server=terminology_server, sct_version="http://snomed.info/sct/83821000000107/version/20190807")
concepts=ConceptsDict(terminology_server=terminology_server)
   
# pickle_filename=os.path.join(  os.environ["SCT_RELEASES"], 
#                                 tag, 
#                                 # "TRIAL_sct_pickle_"+tag
#                                 # "NEW_METHOD_sct_pickle_"+tag
#                                 "RELN_IDS_sct_pickle_"+tag
#                             )
# concepts=release_processing.read_concepts_pickle_file(pickle_filename=pickle_filename, verbose=True)


# ###################################
# # import processed release refset #
# ###################################

# sys.path.append(os.environ["SNOMED_PYTHON"]+"/processing_scripts")
# from process_CLrefsets_UKCL_v34pt1_03aug22 import refsets_release

##############################
# Load refsets from mdb file #
##############################

# msaccess_list=msaccess.get_refset_definitions_from_msaccess_file()
# refsets=refset_module_modified.RefsetCollection()
# for refset_id, description, sctrule, meta in msaccess_list:
#     print("===>>>>",refset_id, description)
#     refsets.append(refset=refset_module_modified.Refset(refset_name=refset_id, refset_description=description, clause_set_string=sctrule, metadata_column=meta))
# refsets.process_filters(concepts=concepts)

refsets=refset_module_modified.RefsetCollection()

# trial_SCT_RULE='<289285006|<<249125003|=12729009|=312974005|=199670005|=169734005|<<267262008|=44223004|<<237267007|'
# trial_SCT_RULE='<<447139008'
trial_SCT_RULE='<<25899002'

# ecl_evaluation=[str(x) for x in terminology_server.do_expand(ecl="^999002121000000109")]
# ecl_evaluation=[str(x) for x in terminology_server.do_expand(ecl="^999002531000000101")]

# trial_SCT_RULE="="+"|=".join(ecl_evaluation)


metadata_column='----------- ----------'
trial_refset=refset_module_modified.Refset(clause_set_string=trial_SCT_RULE, metadata_column=metadata_column, refset_name='trial')

refactor_apply_filters=False

trial_refset.apply_filters=refactor_apply_filters
refsets.append(refset=trial_refset)
refset_list_to_refactor=['trial']  


# sys.exit()

######################################
# Select refset and find all members #
######################################

# refset_name="1127621000000103"
# refset_name="999003211000000103"
# refset_name="1035411000000105"
# refset_name=sys.argv[1]


# refset_list=sys.argv[1]
# if refset_list=="all":
#     refset_list=[r.refset_name for r in refsets]
# else:
#     refset_list=eval(refset_list)

# refset_list_to_refactor=[]

# refsets_to_ignore=["EXCLUDE_LINKAGE_ET_AL", "EXCLUDE_INACTIVE_ET_AL", "EXCLUDE_CLINICALLY_UNLIKELY", "EXCLUDE_DRUGS_ET_AL", "GLOBEX", "GLOBEX_BLOCK"]

# for refset in refset_list:
#     if refset not in refsets_to_ignore:
#         refset_list_to_refactor.append(refset)

for refset_name in refset_list_to_refactor:

    refset=refsets[refsets.refset_name_to_id[refset_name]]

    print(refset)
    print("\n\nSTARTING_REFACTOR: %20s | %s\n\n" % (refset.refset_name, refset.refset_description))
    start_time=time.time()

    # Switch OFF filters  
    refset.apply_filters=refactor_apply_filters

    print("Getting all members ..")
    refset_membership_analysis=refset_module_modified.RefsetMembershipAnalysis(refset=refset, concepts=concepts, global_exclusions=refsets.global_exclusions)
    print(".. done getting all members")

    print("REFSET_INFO:",refset.refset_name, 
                        refset.refset_description, 
                        refset_membership_analysis.full_inclusion_list_n_members, 
                        refset_membership_analysis.full_exclusion_list_n_members, 
                        refset_membership_analysis.final_inclusion_list_n_members
                        )

    ##### temp test
    print("RMA.FIL=", refset_membership_analysis.final_inclusion_list)
    #####

    n_in_refset=len(refset_membership_analysis.final_inclusion_list)
    print("Refset %s contains %s members" % (refset_name, n_in_refset))

    original_include_clause_strings=set()
    original_exclude_clause_strings=set()
    for clause in refset.clause_based_rule.clauses:
        if clause.clause_type=="include":
            original_include_clause_strings.add(clause.clause_base_concept_id)
        if clause.clause_type=="exclude":
            original_exclude_clause_strings.add(clause.clause_base_concept_id)

    print("At start - Original:   %3d include clauses and %3d exclude clauses" % (len(original_include_clause_strings),len(original_exclude_clause_strings)))

    full_refset_members_set      = set(copy.deepcopy(refset_membership_analysis.final_inclusion_list)) # this copy will stay fixed
    trimmed_refset_members_set   = set(copy.deepcopy(refset_membership_analysis.final_inclusion_list)) # this will be whittled down as things are accounted for
    print("Trimmed refset members initially contains %s members" % len(trimmed_refset_members_set))

    required_exclusions_set=set()
    refactored_query=[]

    # problem_incl_id=279390002
    # problem_incl_id=60791006
    # problem_incl_id=105481005
    # problem_incl_id=236973005
    # problem_incl_id=236991000
    problem_incl_id=113343008

    #
    #   NB at some stage need to think how the filtering of refsets will be applied later on
    #

    ######################
    ######################
    # PROCESS INCLUSIONS #
    ######################
    ######################

    ######################################
    # deal with sticky inclusion clauses #
    ######################################

    
    for clause in refset.clause_based_rule.clauses:
        if clause.clause_type=="include" and clause.sticky==True:
            # ? add test for duplcate here?
            #add clause to refactored query
            refactored_query.append(clause)
            #remove concepts captured by clause from trimmed_refset_memebers_set
            concepts_captured_by_clause=set(refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members)
            trimmed_refset_members_set.difference_update(concepts_captured_by_clause)
            #add unwanted concepts to required_exclusions_set
            concepts_captured_that_will_need_exclusion=concepts_captured_by_clause.difference(full_refset_members_set)
            required_exclusions_set.update(concepts_captured_that_will_need_exclusion)

    #############################################
    # deal with modelled (:=) inclusion clauses #
    #############################################

    # this section paused until find out if needs to be implemented

    # allowed_rel_ids=[260507000,255234002,47429007,704321009,263502005,363699004,363700003,704327008,363701004,371881003,
    # 408729009,419066007,418775008,1148969005,736476002,1148967007,840560000,733722007,1142137007,733725009,
    # 836358009,726542003,736472000,736474004,736475003,736473005,827081001,1149366004,363703001,363713009,
    # 411116001,732947008,732945000,719722006,116686009,736518005,1148968002,1149367008,763032000,363710007,
    # 363709002,718497002,704319004,1148965004,272741003,370129005,260686004,246454002,370135005,766939001,
    # 704326004,260870009,408730004,405815000,405816004,363704007,704323007,1003703000,704324001,370130000,
    # 370131001,704325000,719715003,246513007,410675002,370132008,246112005,118171006,118170007,118168003,
    # 118169006,370133003,408732007,424876005,246501002,408731000,726633004,370134009,246514001,425391005,
    # 424226004,424244007,424361007]

    # start_time_modelled_relationships=time.time()
    # concept_ids_modelled_to=set()
    # for concept_id in trimmed_refset_members_set:
    #     concept=concepts[concept_id]
    #     for destination_id, type_ids_list in concept.modelled_relns_as_source.items():
    #         for type_id in type_ids_list:
    #             if type_id in allowed_rel_ids:
    #                 concept_ids_modelled_to.add(destination_id)
    #                 print(concept_id, concept_ids_modelled_to)
    #                 break # once have found one allow typed_id no need to look any further

    # print("Found %s destination ids" % len(concept_ids_modelled_to))

    # print("Modelled_relationships inclusions took (in seconds)", time.time()-start_time_modelled_relationships)

    # sys.exit()

    ################################################
    # make initial catch all set of inclusion cbcs #
    ################################################


    print("Initialising inclusion all_incl_cbcs")

    start_timea=time.time()
    all_inclusion_candidate_base_concept_ids=set()
    for concept_id in trimmed_refset_members_set:
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
        cbc=CandidateBaseConcept(concept_id=concept_id, concepts=concepts, target_members=refset_membership_analysis.final_inclusion_list)
        all_incl_cbcs.add(cbc)
    print("Step2 took (in seconds)", time.time()-start_timeb)    


    print("Initially there are %s cbcs" % len(all_incl_cbcs))

    problem_found=False
    for cbc in all_incl_cbcs:
        if cbc.concept_id==problem_incl_id:
            print("PROBLEM_INCL_ID: %s found" % problem_incl_id)
            problem_found=True
    print("PROBLEM_INCL_ID in initially %s %s" % (problem_incl_id, problem_found))


    to_be_purged_set=set()

    ###############################
    # purge "poor quality" cbcs   #
    ###############################

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
            if cbc.concept_id==problem_incl_id:
                print("PURGING %s reason: %s" % (problem_incl_id, to_be_purged_reason))
            # print("PURGED-REASON:", to_be_purged_reason)
            to_be_purged_set.add(cbc)
        else:
            if cbc.concept_id==problem_incl_id:
                print("NOT PURGING %s : n_in_memb %s | is_perfect_fit %s | n_all %s " % (problem_incl_id, cbc.n_desc_plus_self_in_membership, cbc.is_perfect_fit, cbc.n_desc_plus_self_all))

            pass
            # print("NOT_PURGED")
        # print(to_be_purged_reason)
        # print("========================")
    all_incl_cbcs.difference_update(to_be_purged_set)

    print("After purging poor quality cbcs, %s cbs remain" % len(all_incl_cbcs))
    # for cbc in all_incl_cbcs:
    #     print(cbc)
  

    #########################################################################
    # purge perfect fit cbcs that are subsumed by another perfect fit cbc   #
    #########################################################################

    # 'Delete all redundant candidate ancestors with no true negative descendent ie those also subsumed by another candidate ancestor with no true negative descendent

    
    print("Entering reconstructed loop")
    start_time2=time.time()
    to_be_purged_set=set()
    concepts_ids={cbc.concept_id for cbc in all_incl_cbcs if cbc.is_perfect_fit}
    for cbc in all_incl_cbcs:
        if cbc.is_perfect_fit and (cbc.concept.ancestors.isdisjoint(concepts_ids) is False):
            to_be_purged_set.add(cbc)
    print("Purging %s candidate base concepts that are perfectly subsumed by an ancestor" % len(to_be_purged_set))
    t2=time.time()-start_time2
    print("Purging redundant prefect fit clauses took (in seconds)", time.time()-start_time2)    
    
    # print("Entering time consuming loop")
    # start_time1=time.time()
    # to_be_purged_set=set()
    # for cbc1 in all_incl_cbcs:
    #     for cbc2 in all_incl_cbcs:
    #         if cbc1!=cbc2 and (cbc1.is_perfect_fit) and (cbc2.is_perfect_fit) and (cbc2.concept_id in cbc1.concept.descendants):
    #             to_be_purged_set.add(cbc2)
    # print("Purging %s candidate base concepts that are perfectly subsumed by an ancestor" % len(to_be_purged_set))
    # t1=time.time()-start_time1
    # print("That took (in seconds)", time.time()-start_time1)

    
    # print("TIME_COMP: %.5f %.5f %5s %s | %s" % (t1,t2, to_be_purged_set==new_to_be_purged_set, refset.refset_name, refset.refset_description))



    all_incl_cbcs.difference_update(to_be_purged_set)
    print("That took (in seconds)", time.time()-start_time2)



    ###################################################################
    # separate remaining cbcs into perfect fit and imperfect fit sets #
    ###################################################################

    perfect_fit_incl_cbcs = { cbc for cbc in all_incl_cbcs if cbc.is_perfect_fit==True }
    imperfect_fit_incl_cbcs = all_incl_cbcs.difference(perfect_fit_incl_cbcs)

    print("Provisionally accepted %s candidate base concepts that are perfect fits" % len(perfect_fit_incl_cbcs))
    print("Keeping as candidates %s candidate base concepts that are imperfect fits" % len(imperfect_fit_incl_cbcs))


    # for cbc in perfect_fit_incl_cbcs:
    #     print(cbc.concept_id, cbc.is_perfect_fit, cbc.concept_id in concepts[problem_incl_id].descendants)

    #############################################
    # insert perfect fits into refactored_query #
    #############################################


    for cbc in perfect_fit_incl_cbcs:
        clause_string=cbc.operator+str(cbc.concept_id)
        clause=refset_module_modified.Clause(clause_string)
        refactored_query.append(clause)

    print("REFACTORED_QUERY has length", len(refactored_query))

    ####################################################################################
    # remove concepts that are captured by the clauses in the current refactored query #
    ####################################################################################

    concepts_captured_by_refactored_query=set()
    for clause in refactored_query:
        concepts_captured_by_clause=refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members
        concepts_captured_by_refactored_query.update(concepts_captured_by_clause)
    n_members_captured_by_concepts=len(trimmed_refset_members_set.intersection(concepts_captured_by_refactored_query))
    trimmed_refset_members_set.difference_update(concepts_captured_by_refactored_query)
    print("Refactored query captures %s members" % n_members_captured_by_concepts)
    print("Trimmed refset members now contains remaining %s members" % len(trimmed_refset_members_set))

    ################################
    # main inclusions finding loop #
    ################################

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

    if len(trimmed_refset_members_set)==0: # this is a specific line in DMWB code; not sure completely in line with logic of some of the comment about
                                           # needing to still consider imperfect fit clauses even if all are covered by perfect fit. But that comment may have be superseded by later thoughts.
        terminate_condition_reached=True

    while not terminate_condition_reached:
        iteration+=1
        list_size=len(trimmed_refset_members_set)
        print("\n\nIteration %s :  LSize=%s Fit=%s Z=%s" % (iteration, list_size, fit_threshold, zoom))

        scores=[]
        #Update scores of all remaining cbcs
        for cbc in imperfect_fit_incl_cbcs:
            cbc.set_score(zoom=zoom, verbose=False)
            scores.append((cbc.score, cbc))
            if cbc.concept_id==problem_incl_id:
                print("PROBLEM_INCL SCORE %s %s" % (problem_incl_id, cbc.score))

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
            # c={cbc.concept_id for cbc in imperfect_fit_incl_cbcs}
            # print(len(c), 279390002 in c)
            print("Winner is %s with score %s" % (winner_base_concept.concept_id, winner_cbc.score))
            if len(cbcs_sorted_by_score)>1:
                print("Secondplace is %s with score %s" % (cbcs_sorted_by_score[1].concept_id , cbcs_sorted_by_score[1].score))
            else:
                print("Secondplace: there are no more cbcs in list")
            #Add new clause based on winner to refactored_query and find what concepts it captures
            clause=refset_module_modified.Clause(winner_cbc.clause_string)
            print(winner_cbc.clause_string)
            refactored_query.append(clause)
            n_clauses_added+=1
            concepts_captured_by_clause=refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members
            
            #Remove these captured concepts from the trimmed list
            n_records_to_be_removed_from_trimmed_set=len(trimmed_refset_members_set.intersection(concepts_captured_by_clause))
            trimmed_refset_members_set.difference_update(concepts_captured_by_clause)

            #Add to the required exclusions set any captured concepts that are not in the refset 
            concepts_captured_that_will_need_exclusion=set(concepts_captured_by_clause).difference(set(refset_membership_analysis.final_inclusion_list))
            required_exclusions_set.update(concepts_captured_that_will_need_exclusion)

            #Get rid of winner and its descendants from cbcs
            to_be_purged_set=set()
            for cbc in imperfect_fit_incl_cbcs:
                if cbc.concept_id in winner_base_concept.descendants or cbc==winner_cbc:
                    to_be_purged_set.add(cbc)
            imperfect_fit_incl_cbcs.difference_update(to_be_purged_set)
            print("Purged %s cbcs as descendants of winner or the winner itself" % len(to_be_purged_set))
            
            #Look to see if although found a winner things are being found in clauses that are too small (not convinced by logic here)
            fold_left=float(n_in_refset)/(n_records_to_be_removed_from_trimmed_set+1) # I am not convinced by this section ? intended definition of ClauseCoverage in original code
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
                    fit_threshold = new_fit_threshold
                    zoom = ideal_clause_count
                    winner_exists_at_current_zoom=False
                else:
                    # 'Otherwise we've hit the buffers: the weighting function can't be (de)tuned any further
                    print("TERMINATING: Can't detune inclusion weighting function any further")
                    print("Next best fitting candidate has score of ", new_fit_threshold)
                    print("Minimum fit threshold is ", min_fit_threshold)
                    terminate_condition_reached = True


    print("\nIn loop added %s extra clauses" % n_clauses_added)
    print("REFACTORED_QUERY now has length", len(refactored_query))

    ####################################################################
    # Add unaccounted for concepts as explicit extra inclusion clauses #
    ####################################################################
    print("Adding clauses to cover residue of %s concepts remaining in trimmed list" % len(trimmed_refset_members_set))
    for concept_id in trimmed_refset_members_set:
        if concepts[concept_id].descendants==set():
            operator="<<" # if no descendants use "<<" so that if descendants added they will be included by default
        else:
            operator="=" # else have decendants so use "=" so do not include non members
        clause_string=operator+str(concept_id)
        print("Adding clause", clause_string)
        refactored_query.append(refset_module_modified.Clause(clause_string))

    #####################################
    # Double check if anything left out #
    #####################################
    total_inclusions=set()
    for clause in refactored_query:
        total_inclusions.update(set(refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))
    unaccounted_for=full_refset_members_set.difference(total_inclusions)
    inclusion_check=unaccounted_for==set()
    print("INCLUSION_CHECK:", inclusion_check)
    if not inclusion_check:
        print("ERROR: Exiting as refactored_query does not account for everything")
        sys.exit()

    print("Now require %s exclusions" % len(required_exclusions_set))


    ######################
    ######################
    # REGROUP EXCLUSIONS #
    ######################
    ######################

    problem_id=236973005


    ######################################
    # deal with sticky exclusion clauses #
    ######################################

    for clause in refset.clause_based_rule.clauses:
        if clause.clause_type=="exclude" and clause.sticky==True:
            # ? add test for duplcate here?
            #add clause to refactored query
            refactored_query.append(clause)
            #remove concepts captured by clause from trimmed_refset_memebers_set
            concepts_captured_by_clause=set(refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members)
            required_exclusions_set.difference_update(concepts_captured_by_clause)
            #double check that no sticky clause will exclude refset members (logically it should not as involved in derivation of members list)
            concepts_captured_that_are_in_refset=concepts_captured_by_clause.intersection(full_refset_members_set)
            assert concepts_captured_that_are_in_refset==set()


    ################################################
    # make initial catch all set of exclusion cbcs #
    ################################################

    print("Initialising all_excl_cbcs")
    all_exclusion_candidate_base_concept_ids=set()

    for concept_id in required_exclusions_set:
        all_exclusion_candidate_base_concept_ids.update(concepts[concept_id].ancestors)

    print("PROBLEM_ID: Is %s in required_exclusions_set? %s" % (problem_id, problem_id in all_exclusion_candidate_base_concept_ids))

    # all_exclusion_candidate_base_concept_ids.update(required_exclusions_set)  # trial add in base concepts too
    # test_set=all_exclusion_candidate_base_concept_ids.union(required_exclusions_set)
    # print("test_set is len %s" % len(test_set))
    print("Collated list of %s cbcs in all_exclusion_candidate_base_concept_ids" % len(all_exclusion_candidate_base_concept_ids))
    #remove concepts that are also in ancestors lists of refset members
    n_to_remove=len(all_exclusion_candidate_base_concept_ids.intersection(all_inclusion_candidate_base_concept_ids))
    print("Discarding %s cbcs because also an inclusion ancestor" % n_to_remove)
    all_exclusion_candidate_base_concept_ids.difference_update(all_inclusion_candidate_base_concept_ids)
    print("Now have list of %s cbcs in all_exclusion_candidate_base_concept_ids" % len(all_exclusion_candidate_base_concept_ids))
    print("PROBLEM_ID: Is %s STILL1 in required_exclusions_set? %s" % (problem_id, problem_id in all_exclusion_candidate_base_concept_ids))


    #Now build the all_excl_cbcs
    all_excl_cbcs=set()
    for concept_id in all_exclusion_candidate_base_concept_ids:
        #NOT SURE ABOUT MUST_AVOID_SET logic
        cbc=CandidateBaseConcept(concept_id=concept_id, concepts=concepts, target_members=required_exclusions_set, must_avoid_set=full_refset_members_set)
        all_excl_cbcs.add(cbc)
        # print(cbc)

    print("Initially there are %s exclusion cbcs" % len(all_excl_cbcs))


    ###############################
    # purge "poor quality" cbcs   #
    ###############################

    for cbc in all_excl_cbcs:
        to_be_purged_reason=""
        if cbc.n_desc_plus_self_in_membership<2:
            to_be_purged_reason+="reason1 "
        # if (not cbc.is_perfect_fit):
        #     to_be_purged_reason+="reason2 "

        # test_float=(float(cbc.n_desc_plus_self_in_membership)/cbc.n_desc_plus_self_all)<0.5
        # test_int=(cbc.n_desc_plus_self_all - cbc.n_desc_plus_self_in_membership) > cbc.n_desc_plus_self_in_membership
        # if test_float!=test_int:
        #     print("TEST_DIFFERENCE:", cbc.concept_id, cbc.n_desc_plus_self_all, cbc.n_desc_plus_self_in_membership, float(cbc.n_desc_plus_self_in_membership)/cbc.n_desc_plus_self_all)
        # assert test_float==test_int

        # if (float(cbc.n_desc_plus_self_in_membership)/cbc.n_desc_plus_self_all)<0.5:
        if (cbc.n_desc_plus_self_all - cbc.n_desc_plus_self_in_membership) > cbc.n_desc_plus_self_in_membership:
            to_be_purged_reason+="reason3 "
        # TempDB.Execute "DELETE FROM greedy_ancestors_x WHERE TRUENEG = 1 AND INCLUDE = FALSE AND ALLCHILDREN = 1;"
        if (cbc.n_desc_plus_self_not_in_membership==1 and cbc.is_in_membership==True and cbc.n_children_all==1):
            to_be_purged_reason+="reason4 "
        if to_be_purged_reason != "":
            # print("PURGED-REASON:", to_be_purged_reason)
            if cbc.concept_id==problem_id:
                print("PURGING %s reason: %s" % (problem_id, to_be_purged_reason))
            to_be_purged_set.add(cbc)
        else:
            if cbc.concept_id==problem_id:
                print("NOT PURGING %s : n_in_memb %s | is_perfect_fit %s | n_all %s " % (problem_id, cbc.n_desc_plus_self_in_membership, cbc.is_perfect_fit, cbc.n_desc_plus_self_all))
            pass
            # print("NOT_PURGED")
        # print(to_be_purged_reason)
        # print("========================")
    all_excl_cbcs.difference_update(to_be_purged_set)

    print("After purging poor quality cbcs, %s excl_cbcs remain" % len(all_excl_cbcs))
    # for cbc in all_incl_cbcs:
    #     print(cbc)


    print("PROBLEM_ID: Is %s STILL2 in required_exclusions_set? %s" % (problem_id, problem_id in [cbc.concept_id for cbc in all_excl_cbcs]))


    #########################################################
    # purge excl_cbcs that are subsumed by another excl_cbc #
    #########################################################
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
    print("Now %s excl_cbcs remain" % len(all_excl_cbcs))
    print("That purge took (in seconds)", time.time()-start_time3)

    print("PROBLEM_ID: Is %s STILL3 in required_exclusions_set? %s" % (problem_id, problem_id in [cbc.concept_id for cbc in all_excl_cbcs]))


    ##############################################
    # Try delaying perfect fit check to here to  #
    # see if brings results closer to DMWB       #
    # ############################################

    for cbc in all_excl_cbcs:
        to_be_purged_reason=""
        if (not cbc.is_perfect_fit):
            to_be_purged_reason+="reason2 "
        if to_be_purged_reason != "":
            # print("PURGED-REASON:", to_be_purged_reason)
            if cbc.concept_id==problem_id:
                print("PURGING %s reason: %s" % (problem_id, to_be_purged_reason))
            to_be_purged_set.add(cbc)
        else:
            if cbc.concept_id==problem_id:
                print("NOT PURGING %s : n_in_memb %s | is_perfect_fit %s | n_all %s " % (problem_id, cbc.n_desc_plus_self_in_membership, cbc.is_perfect_fit, cbc.n_desc_plus_self_all))
            pass
        
    all_excl_cbcs.difference_update(to_be_purged_set)

    print("After purging imperfect fit cbcs, %s excl_cbcs remain" % len(all_excl_cbcs))

    ########################################
    # insert clauses into refactored_query #
    ########################################
    total_exclusions=set()
    for cbc in all_excl_cbcs:
        print(cbc.clause_string, cbc.concept.fsn, cbc.n_desc_plus_self_in_membership ,"of", cbc.n_desc_plus_self_all)
        clause=refset_module_modified.Clause("-"+cbc.clause_string)
        refactored_query.append(clause)
        total_exclusions.update(set(refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))
    unaccounted_for_exclusions=required_exclusions_set.difference(total_exclusions) 
    refset_members_hit=full_refset_members_set.intersection(total_exclusions)
    print("REFSET hit: ", len(refset_members_hit))

    ####################################################################
    # Add unaccounted for concepts as explicit extra exclusion clauses #
    ####################################################################
    print("Adding clauses to cover residue of %s concepts remaining in unaccounted_for_exclusions" % len(unaccounted_for_exclusions))
    for concept_id in unaccounted_for_exclusions:
        if concepts[concept_id].descendants==set():
            operator="<<" # if no descendants use "<<" so that if descendants added they will be included by default
        else:
            operator="=" # else have decendants so use "=" so do not include non members
        clause_string="-"+operator+str(concept_id)
        print("Adding clause", clause_string)
        refactored_query.append(refset_module_modified.Clause(clause_string))

    print("Before final clean up query_refactored contains %s clauses" % len(refactored_query))

    ##################
    # Final clean up #
    ##################

    start_time_clean_up=time.time()

    to_be_purged_set=set()

    clause_members_sets=[]
    for i_clause, clause in enumerate(refactored_query):
        clause_members_sets.append(set(refset_module_modified.ClauseMembershipAnalysis(clause=clause, concepts=concepts).members))

    for i_clause2, clause2 in enumerate(refactored_query):
        purge2=False
        to_be_purged_reason=""
        for i_clause1, clause1 in enumerate(refactored_query):
            if clause1.clause_base_concept_id in concepts: # Rather brutal "ignoring"(but not removing) of (sticky) clauses that refer to non existent concepts; need this to stop KeyRrror(s) below.
                if (i_clause1 != i_clause2) and (clause1.clause_type==clause2.clause_type): # NB in DMWB INCLUDE meanes include/exclude for a cluase; but for a (base) concept it means is the concept 
                                                                                            # in the refset (I think)
                #Merge sticky < and = on same concept to a single sticky <<
                # MyDB.Execute "UPDATE QUERY_REFACTORED AS a INNER JOIN QUERY_REFACTORED AS b ON (a.CUI = b.CUI AND a.INCLUDE = b.INCLUDE AND a.EXTENSION = '=' AND b.EXTENSION = '<') SET a.EXTENSION = '<<' WHERE a.STICKY = b.STICKY;"                             
                    if (i_clause2>i_clause1) and (clause1.clause_string==clause2.clause_string): # check for duplicate
                        purge2=True
                        to_be_purged_reason+="DUPLICATE "
                    if (clause1.clause_base_concept_id==clause2.clause_base_concept_id):
                        #Merge sticky < and = on same concept to a single sticky <<
                        # MyDB.Execute "UPDATE QUERY_REFACTORED AS a INNER JOIN QUERY_REFACTORED AS b ON (a.CUI = b.CUI AND a.INCLUDE = b.INCLUDE AND a.EXTENSION = '=' AND b.EXTENSION = '<') SET a.EXTENSION = '<<' WHERE a.STICKY = b.STICKY;"                             
                        if (clause2.clause_operator == "=") and (clause1.clause_operator == "<") and (clause1.sticky==clause2.sticky==True):
                            clause1.clause_operator="<<" # elevate clause1 to "<<"
                                                        # clause2 will then be purged for reason =_WHERE_<<_EXISTS below
                                                        # BUT really should do this for all clauses first before apply code below
                                                        # ***** NB *****   THEREFORE in due course should refactor code to do each purge as a full loop over clauses as in the DMWB code
                        # remove < clauses on a concept if a << clause exists on the same concept;  includes removing a sticky < that is made redundant by a sticky <<
                        if (clause2.clause_operator == "<") and (clause1.clause_operator == "<<") and (clause2.sticky==False or (clause1.sticky==clause2.sticky==True)):
                            purge2=True
                            to_be_purged_reason+="<_WHERE_<<_EXISTS "
                        # remove any = clause made redundant by a << on the same concept; includes removing a sticky = made redundant by a sticky <<
                        if (clause2.clause_operator == "=") and (clause1.clause_operator == "<<") and (clause2.sticky==False or (clause1.sticky==clause2.sticky==True)):
                            purge2=True
                            to_be_purged_reason+="=_WHERE_<<_EXISTS "
                    # remove clauses that are subsumed by another clause with << or < extension; includes removing a sticky clause that is made redundant by another sticky clause
                    # if clause_members_sets[i_clause2] < clause_members_sets[i_clause1]: # this definition retired sep22 in favour of JR's defn of subsumed here based on descendancy
                                        
                    if (clause1.clause_operator in ["<","<<"]) and (clause2.clause_base_concept_id in concepts[clause1.clause_base_concept_id].descendants) and (clause2.sticky==False or (clause1.sticky==clause2.sticky==True)):
                        purge2=True
                        to_be_purged_reason+="SUBSUMED_BY_%s " % i_clause1 
                #Discard any sticky INclusion clauses that are matched by an exactly corresponding sticky EXclusion clause
                if (clause1.clause_base_concept_id==clause2.clause_base_concept_id) and (clause2.clause_type=="include" and clause1.clause_type=="exclude" and clause1.sticky==clause2.sticky==True):
                    test1=clause2.clause_operator == "="  and clause1.clause_operator in ["=","<<"]
                    test2=clause2.clause_operator == "<"  and clause1.clause_operator in ["<","<<"]
                    test3=clause2.clause_operator == "<<" and clause1.clause_operator in ["<<"]
                    if test1 or test2 or test3:
                        purge2=True
                        to_be_purged_reason+="STICKY_INCLUSION_MATCHED_BY_STICKY_EXLCUSION_%s " % i_clause1
        if purge2:
            print(i_clause2, clause2.clause_type, clause2.clause_string,"will be purged. Reason:", to_be_purged_reason)
            to_be_purged_set.add(clause2)
        else:
            # print(i_clause2,"Not purged")
            print(i_clause2, clause2.clause_type, clause2.clause_string,"Not purged")

    purged_refactored_query=[]
    for clause in refactored_query:
        if clause not in to_be_purged_set:
            purged_refactored_query.append(clause)
    refactored_query=purged_refactored_query

    print("After purging, refactored_query contains %s clauses" % len(refactored_query))
    print("CLEAN_UP: took (in seconds)", time.time()-start_time_clean_up)

    for i_clause, clause in enumerate(refactored_query):
        print(i_clause, clause.clause_type, clause.clause_string)

    include_SCTRULE=""
    exclude_SCTRULE=""
    for clause in refactored_query:
        if clause.sticky:
            SCTRULE_stickiness="@"
        else:
            SCTRULE_stickiness=""

        if clause.clause_type=="include":
            include_SCTRULE+= SCTRULE_stickiness + clause.clause_string + "|"
        elif clause.clause_type=="exclude":
            exclude_SCTRULE+= SCTRULE_stickiness + "-" + clause.clause_string + "|"
        else:
            print("ERROR, exiting:invalid clause_type: %s" % clause.clause_type)
            sys.exit()
    if exclude_SCTRULE:
        SCT_RULE= include_SCTRULE + "[" + exclude_SCTRULE
    else:
        SCT_RULE= include_SCTRULE
    print(SCT_RULE)


    ############################################################################
    # do analysis of differences between this method's output and that of DMWB #
    ############################################################################

    refactored_refset=refset_module_modified.Refset(clause_set_string=SCT_RULE, metadata_column=refset.metadata_column)
    # Switch OFF filters  
    refactored_refset.apply_filters=refactor_apply_filters

    refsets.append(refset=refactored_refset)
    refactored_rfa=refset_module_modified.RefsetMembershipAnalysis(refset=refactored_refset, concepts=concepts)
    original_members=set(refset_membership_analysis.final_inclusion_list)
    refactored_members=set(refactored_rfa.final_inclusion_list)

    if (original_members==refactored_members):
        concepts_identical="CONCEPTS_True"
    else:
        concepts_identical="CONCEPTS_False"

    print("\nOriginal refset has %s members" % len(original_members))
    print("Refactored refset has %s members" % len(refactored_members))
    print("\nConcepts in original and not in refactored refset: %s" % original_members.difference(refactored_members))
    print("Concepts in refactored and not in original refset: %s" % refactored_members.difference(original_members))

    # original_include_clause_strings={clause.clause_base_concept_id for clause in refset.clause_based_rule.clauses if clause.clause_type=="include"}
    # original_exclude_clause_strings={clause.clause_base_concept_id for clause in refset.clause_based_rule.clauses if clause.clause_type=="exclude"}

    # refactored_include_clause_strings={clause.clause_base_concept_id for clause in refactored_refset.clause_based_rule.clauses if clause.clause_type=="include"}
    # refactored_exclude_clause_strings={clause.clause_base_concept_id for clause in refactored_refset.clause_based_rule.clauses if clause.clause_type=="exclude"}

    original_include_clause_strings={clause.clause_string for clause in refset.clause_based_rule.clauses if clause.clause_type=="include"}
    original_exclude_clause_strings={clause.clause_string for clause in refset.clause_based_rule.clauses if clause.clause_type=="exclude"}

    refactored_include_clause_strings={clause.clause_string for clause in refactored_refset.clause_based_rule.clauses if clause.clause_type=="include"}
    refactored_exclude_clause_strings={clause.clause_string for clause in refactored_refset.clause_based_rule.clauses if clause.clause_type=="exclude"}

    print("Original:   %3d include clauses and %3d exclude clauses" % (len(original_include_clause_strings),len(original_exclude_clause_strings)))
    print("Refactored: %3d include clauses and %3d exclude clauses" % (len(refactored_include_clause_strings),len(refactored_exclude_clause_strings)))

    include_clauses_only_in_original   =original_include_clause_strings.difference(refactored_include_clause_strings)
    include_clauses_only_in_refactored =refactored_include_clause_strings.difference(original_include_clause_strings)
    exclude_clauses_only_in_original   =original_exclude_clause_strings.difference(refactored_exclude_clause_strings)
    exclude_clauses_only_in_refactored =refactored_exclude_clause_strings.difference(original_exclude_clause_strings)

    ## NB NB NB need to do something about checking stickiness as well!!!!!!!!!!!!!!!!!!!!!!

    if (original_include_clause_strings==refactored_include_clause_strings) and (original_exclude_clause_strings==refactored_exclude_clause_strings):
        clauses_identical="CLAUSES_True"
    else:
        clauses_identical="CLAUSES_False"



    print("")    
    for set_name in ["include_clauses_only_in_original","include_clauses_only_in_refactored","exclude_clauses_only_in_original","exclude_clauses_only_in_refactored"]:
        set_contents=eval(set_name)
        # print(set_name, set_contents)
        if set_contents:
            # for base_concept_id in set_contents:
            for clause_string in set_contents:
                # find the clause with this base_concept_id (bit clunky..)
                # clause_string=None
                base_concept_id=None
                if "original" in set_name:
                    r=refset
                else:
                    r=refactored_refset
                for clause in r.clause_based_rule.clauses:
                    # if clause.clause_base_concept_id==base_concept_id:
                    #     clause_string=clause.clause_string
                    if clause.clause_string==clause_string:
                        base_concept_id=clause.clause_base_concept_id
                print("%34s: %20s %s " % (set_name, clause_string, concepts[base_concept_id].fsn))
        else:
                print("%34s: None" % (set_name))
        print("")    

    print("That took (in seconds)", time.time()-start_time)

    print("\n\nREFACTOR_SUMMARY: %15s %15s | %5d %5d | %3d %3d | %3d %3d | %3d %3d | %3d %3d | %5.1f | %20s | %s \n\n" % (
                                                        concepts_identical,
                                                        clauses_identical,
                                                        len(original_members),
                                                        len(refactored_members),
                                                        len(original_include_clause_strings),
                                                        len(original_exclude_clause_strings),
                                                        len(refactored_include_clause_strings),
                                                        len(refactored_exclude_clause_strings),
                                                        len(include_clauses_only_in_original),
                                                        len(include_clauses_only_in_refactored),
                                                        len(exclude_clauses_only_in_original),
                                                        len(exclude_clauses_only_in_refactored),
                                                        time.time()-start_time,
                                                        refset.refset_name,
                                                        refset.refset_description,
                                                        ))

    print("==============================================================================================")                                            



