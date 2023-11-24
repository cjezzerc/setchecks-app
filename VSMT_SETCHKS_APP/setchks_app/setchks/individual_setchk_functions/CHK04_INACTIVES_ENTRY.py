import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService

from ..check_item import CheckItem

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
        "id_type",
        "implied_concept_id",
        "term",
        "replacement_option_counter",
        "replacement_concept_id",
        "replacement_concept_pt",
        "ambiguity_status",
        "is_replacement_concept_in_set",
        "is_correct_representation_type_in_set",
        }
    
    # class level headers and widths - each different type of supp tab will needs its own SuppTabRow definitions
    headers=[
        "Input row number",
        "Interpretation",
        "Supplied  ID",
        "ID type",	
        "Implied concept Id (if applicable)",
        "Term (TBI)",	
        "Replacement Option Number",	
        "Suggested Concept ID",
        "Preferred Term (if you are certain you want to use Description Ids you can find these by clicking on the link)",
        "Ambiguity status",
        "Is the replacement concept already represented in the set",
        "Is it represented in the list by the same tpe of ID?",
        ]
    cell_widths=[10,20,20,10,20,30,10,20,30,10,10,10]

    
    def __init__(self):
        self.file_row_number=None
        self.interpretation=None
        self.supplied_id=None
        self.id_type=None
        self.implied_concept_id="" # null string so that if not set it shows as a blank
        self.term="TBI"
        self.replacement_option_counter=None
        self.replacement_concept_id=None
        self.replacement_concept_pt=None
        self.ambiguity_status=None
        self.is_replacement_concept_in_set=None
        self.is_correct_representation_type_in_set=None

    def format_as_list(self):
        return [
            f"Row{self.file_row_number}",
            self.interpretation,
            self.supplied_id,
            self.id_type,
            self.implied_concept_id,
            self.term,
            self.replacement_option_counter,
            self.replacement_concept_id,
            self.replacement_concept_pt,
            self.ambiguity_status,
            self.is_replacement_concept_in_set,
            self.is_correct_representation_type_in_set,
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
    for i_data_row, mr in enumerate(setchks_session.marshalled_rows):
        if mr.C_Id is not None:
            concept_id=mr.C_Id
            print(f"concept_id: {concept_id}")
            print(f"mr: {mr}")
            valset_members.add(concept_id)  
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
                                supp_tab_row.id_type="C_Id"
                            else:
                                supp_tab_row.supplied_id=mr.D_Id_entered
                                supp_tab_row.id_type="D_Id"
                                supp_tab_row.implied_concept_id=mr.C_Id
                            supp_tab_row.replacement_option_counter=f"{i_option+1}/{len(hst_options)}"
                            supp_tab_row.replacement_concept_id=hst_option.new_concept_id
                            supp_tab_row.replacement_concept_pt=concepts[hst_option.new_concept_id].pt
                            supp_tab_row.ambiguity_status=hst_option.is_ambiguous
                            supp_tab_row.is_replacement_concept_in_set=supp_tab_row.replacement_concept_id in valset_members
                            if supp_tab_row.is_replacement_concept_in_set is True:
                                supp_tab_row.is_correct_representation_type_in_set=supp_tab_row.id_type in valset_representations_dict[mr.C_Id]
                            else:
                                supp_tab_row.is_correct_representation_type_in_set="-"
                            supp_tab_entries.append(supp_tab_row)
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
                    check_item=CheckItem("CHK04-OUT-i")
                    check_item.outcome_level="INFO"
                    check_item.general_message=(
                        "Concept is active"
                        )
                    this_row_analysis.append(check_item)
                # elif setchk_results.supp_tab_blocks[i_data_row]==[]: #"CHK04-OUT-ii"
                elif interpretations[i_data_row]=="NO_REPLACEMENT": #"CHK04-OUT-ii"
                    if not dual_mode:
                        n_CONCEPTS_INACTIVE+=1
                        n_CONCEPTS_NO_REPLACEMENT+=1
                        check_item=CheckItem("CHK04-OUT-ii-a")
                        check_item.general_message=(
                            "This concept is inactive and should be removed. "
                            "There is no suggested replacement for this concept."
                            )
                        this_row_analysis.append(check_item)
                    else:
                        if active_status_earlier_sct_release[concept_id] is True:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION+=1
                            n_CONCEPTS_NO_REPLACEMENT+=1
                            check_item=CheckItem("CHK04-OUT-ii-b")
                            check_item.general_message=(
                                f"This concept is inactive in the {sct_version.date_string} release and should be removed. "
                                f"It was inactivated since the earlier {earlier_sct_version.date_string} release. "
                                "There is no suggested replacement for this concept."
                                )
                            this_row_analysis.append(check_item)
                        else:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION+=1
                            check_item=CheckItem("CHK04-OUT-ii-c") 
                            check_item.general_message=(
                                f"This concept is inactive in the {sct_version.date_string} release and should be removed. "
                                f"It was already inactive in the earlier {earlier_sct_version.date_string} release. "
                                "There is no suggested replacement for this concept - "
                                "this issue should be resolved via running CHK04 in single version mode"
                                )
                            this_row_analysis.append(check_item)
                else: #"CHK04-OUT-v"
                    if not dual_mode:
                        n_CONCEPTS_INACTIVE+=1
                        n_CONCEPTS_WITH_REPLACEMENTS+=1
                        check_item=CheckItem("CHK04-OUT-v-c")
                        check_item.general_message=(
                            "This concept is inactive and should be removed. "
                            "There is at least one suggested replacement for this concept. "
                            "See supplementary tab for details"
                            )
                        this_row_analysis.append(check_item)
                    else:
                        if active_status_earlier_sct_release[concept_id] is True:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION+=1
                            n_CONCEPTS_WITH_REPLACEMENTS+=1
                            check_item=CheckItem("CHK04-OUT-v-b")
                            check_item.general_message=(
                                f"This concept is inactive in the {sct_version.date_string} release and should be removed. "
                                f"It was inactivated since the earlier {earlier_sct_version.date_string} release. "
                                "There is at least one suggested replacement for this concept. "
                                "See supplementary tab for details"
                                )
                            this_row_analysis.append(check_item)
                        else:
                            n_CONCEPTS_INACTIVE+=1
                            n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION+=1
                            check_item=CheckItem("CHK04-OUT-v-c") 
                            check_item.general_message=(
                                f"This concept is inactive in the {sct_version.date_string} release and should be removed. "
                                f"It was already inactive in the earlier {earlier_sct_version.date_string} release. "
                                "There is at least one suggested replacement for this concept - "
                                "this issue should be resolved via running CHK04 in single version mode "
                                )
                            this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK04-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK04-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
            
    msg=(
    f"There are {n_CONCEPTS_ACTIVE} active concepts in the value set" 
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
    f"There are {n_CONCEPTS_INACTIVE} inactive concepts in the value set "  
    )
    setchk_results.set_analysis["Messages"].append(msg)

    if dual_mode:
        msg=(
        f"{n_CONCEPTS_INACTIVATED_SINCE_EARLIER_SCT_VERSION} concepts in the value set have been newly inactivated since the earlier SCT version" 
        )
        setchk_results.set_analysis["Messages"].append(msg)
        
        msg=(
        f"{n_CONCEPTS_ALSO_INACTIVE_AT_EARLIER_SCT_VERSION} inactive concepts in the value set that were also inactive in the earlier SCT version"  
        )
        setchk_results.set_analysis["Messages"].append(msg)

    if not dual_mode:
        msg=(
        f"{n_CONCEPTS_NO_REPLACEMENT} inactive concepts in the value set have no replacement"  
        )
        setchk_results.set_analysis["Messages"].append(msg)

        msg=(
        f"{n_CONCEPTS_WITH_REPLACEMENTS} inactive concepts in the value set have at least one replacement"  
        )
        setchk_results.set_analysis["Messages"].append(msg)
    else:
        msg=(
        f"{n_CONCEPTS_NO_REPLACEMENT} newly inactivated concepts in the value set have no replacement"  
        )
        setchk_results.set_analysis["Messages"].append(msg)

        msg=(
        f"{n_CONCEPTS_WITH_REPLACEMENTS} newly inactivated concepts in the value set have at least one replacement"  
        )
        setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)