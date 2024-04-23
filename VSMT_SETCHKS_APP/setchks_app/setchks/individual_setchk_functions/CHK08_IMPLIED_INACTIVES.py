import os, copy, sys

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.excel.termbrowser import termbrowser_hyperlink

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow

#
# This was cloned from CHK04 and as few changes as possible were made
# 


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
            assert True, "Should not get here: logic error"
            pass # compared to CHK04 this has no meaning in CHK08 because the new_concept_id is always active
                 # so cannot correspond to a "inactive predecessor with no replacement" 
            # self.interpretation="NO_REPLACEMENT"
        elif self.is_ambiguous=="0":
            self.interpretation="UNAMBIGUOUS"
        else:
            self.interpretation="AMBIGUOUS"

def analyse_hst_data(hst_data=None):
    if len(hst_data)==0: 
        return "NO_IMPLIED_INACTIVES", None 
    hst_option=HstOption(hst_data[0])
    # if hst_option.interpretation=="NO_REPLACEMENT":
    #     return "NO_REPLACEMENT", None
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
        # "eff_time",
        "implied_inactive_option_counter",
        "implied_inactive_concept_id",
        "implied_inactive_concept_pt",
        "implied_inactive_concept_eff_time",
        "ambiguity_status",
        "is_implied_inactive_concept_in_set",
        "is_correct_representation_type_in_set",
        }
    
    # class level headers and widths - each different type of supp tab will needs its own SuppTabRow definitions
    
    headers=[
        "Input row number",
        "Provided Identifier (Active)",
        "Identifier Type",	
        "Corresponding Concept Id (if applicable)",
        "Preferred Term",	
        "",
        "Equivalence of Suggested Inactive Predecessor to Provided Concept",
        "Suggested Inactive Predecessor",
        "Preferred Term",
        "Already in set?",
        # "Effective Time (Active Concept)",
        "Effective Time (Suggested Inactive Concept)"
        ]
    
    # headers=[
    #     "Input row number",
    #     "Interpretation",
    #     "Supplied  Id",
    #     "Id type",	
    #     "Implied concept Id (if applicable)",
    #     "Term (preferred term for this concept - better version TBI)",	
    #     "Implied-inactive Option Number",	
    #     "Implied-inactive Concept Id",
    #     "Preferred Term (if you are certain you want to use Description Ids you can find these by clicking on the link)",
    #     "Ambiguity status",
    #     "Is the implied-inactive concept already represented in the set",
    #     "Is it represented in the list by the same tpe of Id?",
    #     ]
    # cell_widths=[10,20,20,10,20,30,10,20,30,10,10,10]
    # cell_widths=[10,10,20,20,20,30,20,30,10]
    # cell_widths=[10,20,20,20,30,5,24,20,30,10,20,20]
    cell_widths=[10,20,20,20,30,5,24,20,30,10,20]
    YES_NO={True:"Yes", False:"No","-":"-"}
    CONCEPT_DESCRIPTION={"C_Id":"Concept Id", "D_Id":"Description Id"}

    
    def __init__(self):
        self.file_row_number=None
        self.interpretation=None
        self.supplied_id=None
        self.id_type=None
        self.implied_concept_id="" # null string so that if not set it shows as a blank
        self.term=None
        # self.eff_time=None
        self.implied_inactive_option_counter=None
        self.implied_inactive_concept_id=None
        self.implied_inactive_concept_pt=None
        self.implied_inactive_concept_eff_time=None
        self.ambiguity_status=None
        self.is_implied_inactive_concept_in_set=None
        self.is_correct_representation_type_in_set=None
        
    # def format_as_list(self):
    #     return [
    #         f"Row{self.file_row_number}",
    #         self.interpretation,
    #         self.supplied_id,
    #         self.id_type,
    #         self.implied_concept_id,
    #         self.term,
    #         self.implied_inactive_option_counter,
    #         self.implied_inactive_concept_id,
    #         self.implied_inactive_concept_pt,
    #         self.ambiguity_status,
    #         self.is_implied_inactive_concept_in_set,
    #         self.is_correct_representation_type_in_set,
    #         ]
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
            termbrowser_hyperlink(sctid=self.implied_inactive_concept_id),
            self.implied_inactive_concept_pt,
            self.YES_NO[self.is_implied_inactive_concept_in_set],
            # int(self.eff_time),
            int(self.implied_inactive_concept_eff_time),
            ]

        
       
def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "EXTRACT"
    """

    logging.debug("Set Check %s called" % setchk_results.setchk_code)
    print("Set Check %s called" % setchk_results.setchk_code)

    # dual_mode=setchks_session.sct_version_mode=="DUAL_SCT_VERSIONS"
    # if not dual_mode:
    sct_version=setchks_session.sct_version # NB this is an sct_version *object*
    concepts=ConceptsDict(sct_version=sct_version.date_string)
    # else: # in the DUAL_SCT_VERSIONS case the main sct_version is set to the later on (setchks_session.sct_version_b)
    #       # and have earlier_sct_version which is set to setchks_session.sct_version
    #       # the only info needed from the earlier_sct_version is about concept activity
    #     sct_version=setchks_session.sct_version_b
    #     earlier_sct_version=setchks_session.sct_version
    #     concepts=ConceptsDict(sct_version=sct_version.date_string)
    #     concepts_earlier_sct_version=ConceptsDict(sct_version=earlier_sct_version.date_string)

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
    # if dual_mode:
    #     active_status_earlier_sct_release={}

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
            # print(f"concept_id: {concept_id}")
            # print(f"mr: {mr}")
            valset_members.add(concept_id)  
            active_status[concept_id]=concepts[concept_id].active
            # if dual_mode:
                # active_status_earlier_sct_release[concept_id]=concepts_earlier_sct_version[concept_id].active
            if  active_status[concept_id] is True:
                hst_data=hst.get_hst_data_from_new_concept_id(
                    new_concept_id=concept_id, 
                    sct_version=sct_version,
                    )
                # print(concept_id)
                # print(hst_data)
                # print("======================")
                interpretation, hst_options=analyse_hst_data(hst_data=hst_data)
                interpretations[i_data_row]=interpretation
                # if (not dual_mode) or active_status_earlier_sct_release[concept_id] is True:
                # if interpretation=="NO_REPLACEMENT": (see further above re why NO_REPLACEMENT illogical in CHK08)
                #     supp_tab_entries=[]
                # else: 
                supp_tab_entries=[]
                if hst_options:
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
                        # supp_tab_row.eff_time=concepts[concept_id].effective_time

                        supp_tab_row.implied_inactive_option_counter=f"{i_option+1}/{len(hst_options)}"
                        supp_tab_row.implied_inactive_concept_id=hst_option.old_concept_id
                        supp_tab_row.implied_inactive_concept_pt=concepts[hst_option.old_concept_id].pt
                        supp_tab_row.implied_inactive_concept_eff_time=concepts[hst_option.old_concept_id].effective_time
                        supp_tab_row.ambiguity_status=hst_option.is_ambiguous
                        supp_tab_row.is_implied_inactive_concept_in_set=supp_tab_row.implied_inactive_concept_id in valset_members
                        if supp_tab_row.is_implied_inactive_concept_in_set is True:
                            supp_tab_row.is_correct_representation_type_in_set=supp_tab_row.id_type in valset_representations_dict[mr.C_Id]
                        else:
                            supp_tab_row.is_correct_representation_type_in_set="-"
                        supp_tab_entries.append(supp_tab_row)
                else: # has no predecessors
                    supp_tab_entries=None

            else: # if inactive
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
    n_CONCEPTS_NO_IMPLIED_INACTIVES=0
    n_CONCEPTS_WITH_IMPLIED_INACTIVES=0


    for i_data_row,mr in enumerate(setchks_session.marshalled_rows):
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                if active_status[concept_id] is False: 
                    n_CONCEPTS_INACTIVE+=1
                    #<check_item>
                    check_item=CheckItem("CHK08-OUT-01") # formerly vi
                    check_item.outcome_level="DEBUG"
                    check_item.general_message=(
                        "This Concept is inactive"
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
                elif interpretations[i_data_row]=="NO_IMPLIED_INACTIVES": 
                    n_CONCEPTS_ACTIVE+=1
                    n_CONCEPTS_NO_IMPLIED_INACTIVES+=1
                    #<check_item>
                    check_item=CheckItem("CHK08-OUT-02") # formerly i
                    check_item.outcome_level="DEBUG"
                    check_item.general_message=(
                        "This active Concept has no inactive predecessors. "
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
                
                else: 
                    
                    n_CONCEPTS_ACTIVE+=1
                    n_CONCEPTS_WITH_IMPLIED_INACTIVES+=1
                    #<check_item>
                    check_item=CheckItem("CHK08-OUT-03") # formerly vii
                    check_item.outcome_level="ISSUE"
                    check_item.general_message=(
                        "This active Concept has possible inactive predecessors that should be considered for inclusion "
                        "since, according to your settings, this is a data extraction value set. "
                        "See 'CHK08_suppl' tab for details."
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
                 
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                #<check_item>
                check_item=CheckItem("CHK08-OUT-NOT_FOR_PRODUCTION")
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
            check_item=CheckItem("CHK08-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            this_row_analysis.append(check_item)
            #</check_item>



    if n_CONCEPTS_WITH_IMPLIED_INACTIVES==0:
        #<set_level_message>
       setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            simple_message=(
                "[GREEN] This check has detected no issues."
                ),
            outcome_code="CHK08-OUT-08",
            )
        ) 
        #</set_level_message>
    else:
        #<set_level_message>
       setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            simple_message=(
                "[AMBER] You should study the information provided about possible inactive predecessors. "
                "This check has identified inactive codes that probably mean the same as some of the codes in your list "
                "and that could be in the data you want to extract from. " 
                "Having the fullest set of firmly identified inactive predecessors for each active concept "
                "will generally improve the quality of data extraction. Currently this check does not "
                "attempt to assess the coverage of possible inactive predecessors already in the "
                "value set."
                ),
            outcome_code="CHK08-OUT-04",
            )
        ) 
        #</set_level_message>
       
    
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows with an active Concept that has no inactive predecessors"
                ),
            value=f"{n_CONCEPTS_NO_IMPLIED_INACTIVES}",
            outcome_code="CHK08-OUT-06",
            )
        ) 
    #</set_level_count>
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows with an active Concept that has at least one possible inactive predecessor"
                ),
            value=f"{n_CONCEPTS_WITH_IMPLIED_INACTIVES}",
            outcome_code="CHK08-OUT-07",
            )
        )
    #</set_level_count>
    #<set_level_count>
    setchk_results.set_level_table_rows.append(
        SetLevelTableRow(
            descriptor=(
                "Number of rows with an inactive Concept"
                ),
            value=f"{n_CONCEPTS_INACTIVE}",
            outcome_code="CHK08-OUT-05",
            )
        )  
    #</set_level_count>
     