import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.excel.termbrowser import termbrowser_hyperlink

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow


class HstOption():
    __slots__={
        "old_concept_id", # for completeness sake but should be clear from context
        "old_concept_status",
        "new_concept_id",
        "new_concept_status",
        "path",
        "is_ambiguous",
        "iterations",
        "interpretation"
        }
    def __init__(self, hst_entry=None):
        self.old_concept_id=hst_entry["old_concept_id"]
        self.old_concept_status=hst_entry["old_concept_status"]
        self.new_concept_id=hst_entry["new_concept_id"]
        self.new_concept_status=hst_entry["new_concept_status"]
        self.path=hst_entry["path"]
        self.is_ambiguous=hst_entry["is_ambiguous"]
        self.iterations=hst_entry["iterations"]
        if self.old_concept_id==self.new_concept_id:
            self.interpretation="NO_REPLACEMENT"
        elif self.is_ambiguous=="0":
            self.interpretation="UNAMBIGUOUS"
        else:
            self.interpretation="AMBIGUOUS"

def analyse_hst_data(hst_data=None):
    if len(hst_data)==0: # should not really happen but this would be if e.g. passed in hst_data for an active concept
        return None, None 
    hst_option=HstOption(hst_data[0])
    if hst_option.interpretation=="NO_REPLACEMENT":
        return "NO_REPLACEMENT", None
    if hst_option.interpretation=="UNAMBIGUOUS":
        return "UNAMBIGUOUS", [hst_option]
    # otherwise must be ambiguous
    hst_options=[]
    for hst_entry in hst_data:
        hst_options.append(HstOption(hst_entry))
    return "AMBIGUOUS", hst_options

class SuppTabRow():
    __slots__={
        "file_row_number",
        "interpretation",
        "supplied_id",
        "supplied_id_as_possible_link",
        "id_type",
        "implied_concept_id",
        "term",
        "eff_time",
        "replacement_option_counter",
        "replacement_concept_id",
        "replacement_concept_pt",
        # "replacement_concept_eff_time",
        "ambiguity_status",
        "is_replacement_concept_in_set",
        "is_correct_representation_type_in_set",
        }
    YES_NO={True:"Yes", False:"No","-":"-"}
    CONCEPT_DESCRIPTION={"C_Id":"Concept Id", "D_Id":"Description Id"}

    # class level headers and widths - each different type of supp tab will needs its own SuppTabRow definitions
    headers=[
        "Input row number",
        "Provided Identifier (Inactive)",
        "Identifier Type",	
        "Corresponding Concept Id (if applicable)",
        "Preferred Term",	
        "",
        "Equivalence of Suggested Concept to Provided Concept",
        "Suggested Concept Id (Active)",
        "Preferred Term",
        "Already in set",
        "Effective Time (Inactive Concept)",
        # "Effective Time (Suggested Active Concept)",
        ]
    # cell_widths=[10,20,20,20,30,5,24,20,30,10,20,20]
    cell_widths=[10,20,20,20,30,5,24,20,30,10,20]

    
    def __init__(self):
        self.file_row_number=None
        self.interpretation=None
        self.supplied_id=None
        self.supplied_id_as_possible_link=None
        self.id_type=None
        self.implied_concept_id="" # null string so that if not set it shows as a blank
        self.term=None
        self.eff_time=None
        self.replacement_concept_id=None
        self.replacement_concept_pt=None
        # self.replacement_concept_eff_time=None
        self.ambiguity_status=None
        self.is_replacement_concept_in_set=None
        self.is_correct_representation_type_in_set=None
    

    def format_as_list(self):
        ambiguity_status_words={
            "0":"No ambiguity",
            "1":"Possible ambiguity",
            "2":"Loss of precision",
            "3":"Definite ambiguity",
        }
        return [
            f"Row {self.file_row_number}",
            # f"HST-{self.ambiguity_status}",
            self.supplied_id,
            self.CONCEPT_DESCRIPTION[self.id_type],
            # self.implied_concept_id,
            termbrowser_hyperlink(sctid=self.implied_concept_id),
            self.term,
            # self.replacement_option_counter,
            # self.replacement_concept_id,
            "-->",
            ambiguity_status_words[self.ambiguity_status],
            termbrowser_hyperlink(sctid=self.replacement_concept_id),
            self.replacement_concept_pt,
            self.YES_NO[self.is_replacement_concept_in_set],
            int(self.eff_time),
            # int(self.replacement_concept_eff_time),
            ]

        
       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "ENTRY_PRIMARY"
        "ENTRY_OTHER"
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    dual_mode=setchks_session.sct_version_mode=="DUAL_SCT_VERSIONS"
    if not dual_mode:
        sct_version=setchks_session.sct_version # NB this is an sct_version *object*
        concepts=ConceptsDict(sct_version=sct_version.date_string)
    else: # in the DUAL_SCT_VERSIONS case the main sct_version is set to the later on (setchks_session.sct_version_b)
          # and have earlier_sct_version which is set to setchks_session.sct_version
          # the only info needed from the earlier_sct_version is about concept activity
        sct_version=setchks_session.sct_version_b
        earlier_sct_version=setchks_session.sct_version
        concepts=ConceptsDict(sct_version=sct_version.date_string)
        concepts_earlier_sct_version=ConceptsDict(sct_version=earlier_sct_version.date_string)

    hst=DescriptionsService(data_type="hst")

    ###########################################################################
    # First pass over all rows to build up membership and supp                #
    # tab rows so that can reference things correctly when do second pass     #     
    ###########################################################################
   
    
    valset_members=set()
    valset_representations_dict={}  # keyed by concept_id
                                    # each entry a set of representation types that are seem for this concept in the set
                                    # i.e. ("C_Id"),("D_Id") or ("C_Id","D_Id") 
                                    # this is used to make sure the right "type" of replacement is checked for already being in set
    active_status={} # keyed by concept Id
                     # values is True if active
    if dual_mode:
        active_status_earlier_sct_release={}

    for mr in setchks_session.marshalled_rows:
            concept_id=mr.C_Id
            if concept_id is not None:
                valset_members.add(concept_id)
                if concept_id not in valset_representations_dict:
                    valset_representations_dict[concept_id]=set()
                if mr.C_Id_entered is not None:
                    valset_representations_dict[concept_id].add("C_Id")
                if mr.C_Id_entered is not None:
                    valset_representations_dict[concept_id].add("D_Id")

    setchk_results.supp_tab_blocks=[] # there will be one entry in list for each data row
                    # each entry will either be None(active entries) or a list(B) of supp_tab_row objects
                    # if there are no replacements the list(B) will be []
    interpretations={} 
    # unambiguous_replacement_is_in_valset={} # keyed by i_data_row; value is always just True (ie essentially is a set)
    
    # Next two counters are computed earlier than the others. These counters were added later and are to give an
    # indication to the user of how many "easy cases" already sorted out.
    # These two counters apply in both the single and dual case. Int he dual case thye only apply to things inactivated
    # since earlier release.
    N_CONCEPTS_WITH_UNAMBIG_REPL=0
    N_CONCEPTS_WITH_UNAMBIG_REPL_WITH_REPL_IN_VALSET=0
    
    for i_data_row, mr in enumerate(setchks_session.marshalled_rows):
        if mr.C_Id is not None:
            concept_id=mr.C_Id 
            # valset_members.add(concept_id)  # this is not needed as done in loop above
            active_status[concept_id]=concepts[concept_id].active
            if dual_mode:
                active_status_earlier_sct_release[concept_id]=concepts_earlier_sct_version[concept_id].active
            if  active_status[concept_id] is False:
                hst_data=hst.get_hst_data_from_old_concept_id(
                    old_concept_id=concept_id, 
                    sct_version=sct_version,
                    )
                interpretation, hst_options=analyse_hst_data(hst_data=hst_data)
                interpretations[i_data_row]=interpretation
                if (not dual_mode) or active_status_earlier_sct_release[concept_id] is True:
                    if interpretation=="NO_REPLACEMENT":
                        supp_tab_entries=[]
                    else: 
                        supp_tab_entries=[]
                        for i_option, hst_option in enumerate(hst_options):
                            supp_tab_row=SuppTabRow()
                            supp_tab_row.file_row_number=setchks_session.first_data_row+i_data_row+1
                            supp_tab_row.interpretation=hst_option.interpretation
                            if mr.C_Id_entered is not None:
                                supp_tab_row.supplied_id=mr.C_Id_entered
                                # supp_tab_row.supplied_id_as_possible_link=termbrowser_hyperlink(sctid=supp_tab_row.supplied_id)
                                supp_tab_row.id_type="C_Id"
                            else:
                                supp_tab_row.supplied_id=mr.D_Id_entered 
                                supp_tab_row.id_type="D_Id"
                                supp_tab_row.implied_concept_id=mr.C_Id
                            # propose set supp_tab.term via
                            # if setchks_session.columns_info.have_dterm_column:
                            #     if mr.C_Id_entered is not None and mr.congruence_of_C_Id_entered_and_D_Term_entered_csr:
                            #         supp_tab_row.term=mr.D_Term_entered
                            #     else:
                            #         supp_tab_row.term=concepts[concept_id].pt
                            #     if mr.D_Id_entered is not None and mr.congruence_of_D_Id_entered_and_D_Term_entered_csr:
                            #         supp_tab_row.term=mr.D_Term_entered
                            #     else:
                            #         supp_tab_row.term=mr.D_Term_derived_from_D_Id_entered
                            # elif mr.D_Id_entered is not None:
                            #     supp_tab_row.term=mr.D_Term_derived_from_D_Id_entered
                            # else:
                            #     supp_tab_row.term=concepts[concept_id].pt
                            # but for familiarisation day 2 just do (as no time to test the above)
                            supp_tab_row.term=concepts[concept_id].pt
                            supp_tab_row.eff_time=concepts[concept_id].effective_time

                            # if mr.C_Id_entered is not None and mr.congruence_of_C_Id_entered_and_D_Term_entered_csr
                            # if mr.D_Id_entered is not None and mr.congruence_of_C_Id_entered_and_D_Term_entered_csr
                            supp_tab_row.replacement_option_counter=f"{i_option+1}/{len(hst_options)}"
                            supp_tab_row.replacement_concept_id=hst_option.new_concept_id
                            supp_tab_row.replacement_concept_pt=concepts[hst_option.new_concept_id].pt
                            # supp_tab_row.replacement_concept_eff_time=concepts[hst_option.new_concept_id].effective_time
                            supp_tab_row.ambiguity_status=hst_option.is_ambiguous
                            supp_tab_row.is_replacement_concept_in_set=supp_tab_row.replacement_concept_id in valset_members
                            if supp_tab_row.is_replacement_concept_in_set is True:
                                supp_tab_row.is_correct_representation_type_in_set=supp_tab_row.id_type in valset_representations_dict[mr.C_Id]
                            else:
                                supp_tab_row.is_correct_representation_type_in_set="-"
                            supp_tab_entries.append(supp_tab_row)
                            if interpretation=="UNAMBIGUOUS":
                                N_CONCEPTS_WITH_UNAMBIG_REPL+=1
                                if supp_tab_row.is_replacement_concept_in_set is True:
                                    N_CONCEPTS_WITH_UNAMBIG_REPL_WITH_REPL_IN_VALSET+=1
                else: # it's inactive but also was inactive in earlier_sct_version so not reported
                    supp_tab_entries=None
            else: # if active
                supp_tab_entries=None
        else: # if e.g. a rogue entry that should not have got past the gatekeeper (assume this only happens in dev)
            supp_tab_entries=None

        setchk_results.supp_tab_blocks.append(supp_tab_entries)



    ##################################################################
    ##################################################################
    ##################################################################
    #           Test concept on each row of value set                #     
    ##################################################################
    ##################################################################
    ##################################################################
    
    n_FILE_TOTAL_ROWS=setchks_session.first_data_row
    n_FILE_PROCESSABLE_ROWS=0
    n_FILE_NON_PROCESSABLE_ROWS=setchks_session.first_data_row  # with gatekeeper this is just blank or header rows
    
    n_CONCEPTS_ACTIVE=0
    n_CONCEPTS_INACTIVE=0
    if dual_mode:
        n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION=0
        n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION=0
    n_CONCEPTS_NO_REPLACEMENT=0
    n_CONCEPTS_WITH_REPLACEMENTS=0

    if setchks_session.data_entry_extract_type !="EXTRACT":
        retain_and_or_replace_advice_message=(
            "According to your settings, this is a data entry value set. " 
            "All inactive Concepts should be removed, and replaced where possible."
            )
    else:
        retain_and_or_replace_advice_message=(
            "According to your settings, this is a data extraction value set. " 
            "All inactive Concepts should be retained, and active replacement Concepts added where possible."
            )

    for i_data_row,mr in enumerate(setchks_session.marshalled_rows):
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                # if setchk_results.supp_tab_blocks[i_data_row] is None: #"CHK04-OUT-i"
                if active_status[concept_id] is True: #"CHK04-OUT-i"
                    n_CONCEPTS_ACTIVE+=1
                    #<check_item>
                    check_item=CheckItem("CHK04-OUT-23") # was CHK04-OUT-i
                    check_item.outcome_level="DEBUG"
                    check_item.general_message=(
                        "Concept is active"
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
                # elif setchk_results.supp_tab_blocks[i_data_row]==[]: 
                elif interpretations[i_data_row]=="NO_REPLACEMENT": 
                    if not dual_mode:
                        n_CONCEPTS_INACTIVE+=1
                        n_CONCEPTS_NO_REPLACEMENT+=1
                        #<check_item>
                        check_item=CheckItem("CHK04-OUT-24") # was CHK04-OUT-ii-a
                        check_item.outcome_level="ISSUE"
                        check_item.general_message=(
                            f"This Concept is inactive. {retain_and_or_replace_advice_message} "
                            "There is no suggested replacement for this Concept."
                            )
                        #</check_item>
                        this_row_analysis.append(check_item)
                    else:
                        if active_status_earlier_sct_release[concept_id] is True:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION+=1
                            n_CONCEPTS_NO_REPLACEMENT+=1
                            #<check_item>
                            check_item=CheckItem("CHK04-OUT-25") # was CHK04-OUT-ii-b
                            check_item.outcome_level="ISSUE"
                            check_item.general_message=(
                                f"This Concept is inactive in the {sct_version.date_string} release. {retain_and_or_replace_advice_message} "
                                f"It was inactivated since the earlier {earlier_sct_version.date_string} release. "
                                "There is no suggested replacement for this Concept."
                                )
                            #</check_item>
                            this_row_analysis.append(check_item)
                        else:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION+=1
                            #<check_item>
                            check_item=CheckItem("CHK04-OUT-26") # was CHK04-OUT-ii-c
                            check_item.outcome_level="ISSUE"
                            check_item.general_message=(
                                f"This Concept is inactive in the {sct_version.date_string} release. {retain_and_or_replace_advice_message} "
                                f"It was already inactive in the earlier {earlier_sct_version.date_string} release. "
                                "There is no suggested replacement for this Concept - "
                                "this issue should be resolved by running CHK04 in Single Release mode."
                                )
                            #</check_item>
                            this_row_analysis.append(check_item)
                else: #"CHK04-OUT-v"
                    if not dual_mode:
                        n_CONCEPTS_INACTIVE+=1
                        n_CONCEPTS_WITH_REPLACEMENTS+=1
                        #<check_item>
                        check_item=CheckItem("CHK04-OUT-27") # was CHK04-OUT-v-a
                        check_item.outcome_level="ISSUE"
                        check_item.general_message=(
                            f"This Concept is inactive. {retain_and_or_replace_advice_message} "
                            "There is at least one suggested replacement for this Concept. "
                            "See 'CHK04_suppl' tab for details."
                            )
                        #</check_item>
                        this_row_analysis.append(check_item)
                    else:
                        if active_status_earlier_sct_release[concept_id] is True:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION+=1
                            n_CONCEPTS_WITH_REPLACEMENTS+=1
                            #<check_item>
                            check_item=CheckItem("CHK04-OUT-28") # was CHK04-OUT-v-b
                            check_item.outcome_level="ISSUE"
                            check_item.general_message=(
                                f"This Concept is inactive in the {sct_version.date_string} release. {retain_and_or_replace_advice_message} "
                                f"It was inactivated since the earlier {earlier_sct_version.date_string} release. "
                                "There is at least one suggested replacement for this concept. "
                                "See 'CHK04_suppl' tab for details."
                                )
                            #</check_item>
                            this_row_analysis.append(check_item)
                        else:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION+=1
                            #<check_item>
                            check_item=CheckItem("CHK04-OUT-29") # was CHK04-OUT-v-c
                            check_item.outcome_level="ISSUE"
                            check_item.general_message=(
                                f"This Concept is inactive in the {sct_version.date_string} release. {retain_and_or_replace_advice_message} "
                                f"It was already inactive in the earlier {earlier_sct_version.date_string} release. "
                                "There is at least one suggested replacement for this Concept - "
                                "this issue should be resolved by running CHK04 in Single Release mode."
                                )
                            #</check_item>
                            this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                #<check_item>
                check_item=CheckItem("CHK04-OUT-NOT_FOR_PRODUCTION")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                #</check_item>
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            #<check_item>
            check_item=CheckItem("CHK04-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)
            #</check_item>

    setchk_results.set_analysis["Messages"]=[] 

    if not dual_mode:
        if n_CONCEPTS_INACTIVE==0:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                simple_message=(
                    "[GREEN] This check has detected no issues."
                    ),
                outcome_code="CHK04-OUT-19"
                )
            )
            #</set_level_message>
        else:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                simple_message=(
                    "[RED] This value set includes inactive Concepts. "
                    f"{retain_and_or_replace_advice_message}"
                    ),
                outcome_code="CHK04-OUT-16",
                )
            )
            #</set_level_message>

            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    "Number of inactive Concepts "
                    ),
                value=f"{n_CONCEPTS_INACTIVE}",
                outcome_code="CHK04-OUT-09",
                )
            )
            #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    "Number of inactive Concepts with at least one replacement "
                    ),
                value=f"{n_CONCEPTS_WITH_REPLACEMENTS}",
                outcome_code="CHK04-OUT-12",
                )
            )
            #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    "Number of inactive Concepts with no replacement "
                    ),
                value=f"{n_CONCEPTS_NO_REPLACEMENT}",
                outcome_code="CHK04-OUT-11",
                )
            )
            #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    'Number of inactive Concepts with a "No ambiguity" replacement '
                    ),
                value=f"{N_CONCEPTS_WITH_UNAMBIG_REPL}",
                outcome_code="CHK04-OUT-01",
                )
            )
            #</set_level_count>
                        #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    'Number of inactive Concepts with a "No ambiguity" replacement where the replacement is already in the value set'
                    ),
                value=f"{N_CONCEPTS_WITH_UNAMBIG_REPL_WITH_REPL_IN_VALSET}",
                outcome_code="CHK04-OUT-02",
                )
            )
            #</set_level_count>
            
    else: # dual mode
        if n_CONCEPTS_INACTIVE==0:
            #<set_level_message>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                simple_message=(
                    "[GREEN] No inactive concepts have been detected using the later release"
                    ),
                outcome_code="CHK04-OUT-20",
                )
            )
            #</set_level_message>
        else:
            if n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION>0:
                #<set_level_message>
                setchk_results.set_level_table_rows.append(
                        SetLevelTableRow(
                        simple_message=(
                            "[RED] This value set includes Concepts that are inactive in the later release, " 
                            "and that were inactivated since the earlier release."
                            f"{retain_and_or_replace_advice_message}"
                            ),
                        outcome_code="CHK04-OUT-18",
                        )
                    )
                #</set_level_message>
                #<set_level_count>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                    descriptor=(
                        "Number of Concepts inactivated since the earlier release"
                        ),
                    value=f"{n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION}",
                    outcome_code="CHK04-OUT-14",
                    )
                )
                #</set_level_count>
                #<set_level_count>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                    descriptor=(
                        "Number of newly inactivated Concepts with at least one replacement "
                        ),
                    value=f"{n_CONCEPTS_WITH_REPLACEMENTS}",
                    outcome_code="CHK04-OUT-21",
                    )
                )
                #</set_level_count>
                #<set_level_count>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                    descriptor=(
                        "Number of newly inactivated Concepts with no replacement "
                        ),
                    value=f"{n_CONCEPTS_NO_REPLACEMENT}",
                    outcome_code="CHK04-OUT-22",
                    )
                )
                #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    'Number of newly inactivated Concepts with a "No ambiguity" replacement '
                    ),
                value=f"{N_CONCEPTS_WITH_UNAMBIG_REPL}",
                outcome_code="CHK04-OUT-03",
                )
            )
            #</set_level_count>
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                descriptor=(
                    'Number of newly inactivated Concepts with a "No ambiguity" replacement where the replacement is already in the value set'
                    ),
                value=f"{N_CONCEPTS_WITH_UNAMBIG_REPL_WITH_REPL_IN_VALSET}",
                outcome_code="CHK04-OUT-04",
                )
            )
            #</set_level_count>
            if n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION>0:
                #<set_level_message>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                    simple_message=(
                        "[RED] When running in Dual Release mode the checks are focussed primarily on "
                        "changes that have occurred between the two releases."
                        "This value set contains Concepts that are inactive in "
                        "both the earlier and later releases. For such Concepts, " 
                        "this report will only provide basic information, "
                        "and does not suggest possible replacements."
                        "It is recommended that you should run your value set in Single Release mode "
                        "using the earlier release and act on the information provided. " 
                        "Then re-run the updated value set in Dual Release mode."
                        ),
                    outcome_code="CHK04-OUT-17"
                    )
                )
                #</set_level_message>
                #<set_level_count>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                    descriptor=(
                        "Number of inactive Concepts that were also inactive in the earlier release"
                        ),
                    value=f"{n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION}",
                    outcome_code="CHK04-OUT-15",
                    )
                )
                #</set_level_count>
