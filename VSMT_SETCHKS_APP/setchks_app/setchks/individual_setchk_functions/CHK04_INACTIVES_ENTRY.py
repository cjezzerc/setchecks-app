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
        "i_data_row",
        "interpretation"
        "supplied_id",
        "id_type",
        "id_type",
        "replacement_option_counter",
        "replacement_concept_id",
        "replacement_concept_pt",
        "ambiguity_status",
        "is_replacement_concept_in_set",
        "is_correct_representation_type_in_set"
        }
    
    def __init__(self):
        self.i_data_row=None
        self.interpretation=None
        self.supplied_id==None
        self.id_type==None
        self.replacement_option_counter==None
        self.replacement_concept_id==None
        self.replacement_concept_pt==None
        self.ambiguity_status==None
        self.is_replacement_concept_in_set==None
        self.is_correct_representation_type_in_set==None

    def format_as_list(self):
        return [
            f"Row{self.i_data_row}",
            self.interpretation,
            self.supplied_id,
            self.id_type,
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

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)
    hst=DescriptionsService(data_type="hst")

    ##################################################################
    ##################################################################
    ##################################################################
    # Analyse membership against the top level hierarchies           #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    
    valset_members=set()
    active_status={} # keyed by concept Id
                     # values is True if active
    for mr in setchks_session.marshalled_rows:
        if mr.C_Id is not None:
            concept_id=mr.C_Id
            valset_members.add(concept_id)  
            active_status[concept_id]=concepts[concept_id].active
            if active_status[concept_id] is False:
                hst_data=hst.get_hst_data_from_old_concept_id(old_concept_id=concept_id, sct_version=setchks_session.sct_version)
                interpretation, hst_options=analyse_hst_data(hst_data=hst_data)
                if interpretation=="NO_REPLACEMENT":
                    supp_tab_entries=None
                else interpretation=="UNAMBIGUOUS":
                    supp_tab_entries=[]
                    for i_option, hst_option in enumerate(hst_options):
                        supp_tab_row=SuppTabRow()
                        supp_tab_row.interpretation=hst_option.interpretation
                        if mr.C_Id_entered is not None:
                            self.supplied_id=mr.C_Id_entered
                            self.id_type="C_Id"
                        else:
                            self.supplied_id=mr.C_Id_entered
                            self.id_type="D_Id"
                        self.replacement_option_counter=f"{i_option}/{len(hst_options)}"
                        self.replacement_concept_id, ##### GOT TO HERE
                        self.replacement_concept_pt,
                        self.ambiguity_status,
                        self.is_replacement_concept_in_set,
                        self.is_correct_representation_type_in_set,

                print(f"{concept_id}: {interpretation} {hst_option_data}")

            
    print(f"valset_members {valset_members}")
    sys.exit()

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
    
    n_CONCEPTS_IN_DOMAIN={}
    for id in domain_ids:
        n_CONCEPTS_IN_DOMAIN[id]=0
    n_CONCEPTS_NOT_RECOMMENDED=0
    n_CONCEPTS_MAY_NOT_BE_APPROPRIATE=0
    n_CONCEPTS_ACCEPTABLE=0

    data_entry_extract_type=setchks_session.data_entry_extract_type
    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                for domain_id in domain_ids:
                    domain_name=id_to_full_domain_name_dict[domain_id]
                    print(concept_id,type(concept_id), domain_id, domain_name, valset_members_in_domain_dict[domain_id])
                    if concept_id in valset_members_in_domain_dict[domain_id]:
                        acceptability=acceptability_dicts_by_id[data_entry_extract_type][domain_id]
                        n_CONCEPTS_IN_DOMAIN[domain_id]+=1
                        if acceptability=="ACCEPTABLE": #"CHK05-OUT-01"
                            n_CONCEPTS_ACCEPTABLE+=1
                            check_item=CheckItem("CHK05-OUT-01")
                            check_item.outcome_level="INFO"
                            check_item.general_message=(
                                "OK"
                                )
                            this_row_analysis.append(check_item)
                        elif acceptability=="MAY_NOT_BE_APPROPRIATE": #"CHK05-OUT-02"
                            n_CONCEPTS_MAY_NOT_BE_APPROPRIATE+=1
                            check_item=CheckItem("CHK05-OUT-02")
                            check_item.general_message=(
                                f"The Concept Id is a subtype of the {domain_name} hierarchy in SNOMED CT." 
                                f"The hierarchy has been categorised as ‘may not be appropriate’ for the "
                                f"{data_entry_extract_type} data entry type assigned to this value set."
                                )
                            this_row_analysis.append(check_item)
                        elif acceptability=="NOT_RECOMMENDED": #"CHK05-OUT-03"
                            n_CONCEPTS_NOT_RECOMMENDED+=1
                            check_item=CheckItem("CHK05-OUT-03")
                            check_item.general_message=(
                                f"The Concept Id is a subtype of the {domain_name} hierarchy in SNOMED CT." 
                                f"The hierarchy has been categorised as ‘not recommended’ for the "
                                f"{data_entry_extract_type} data entry type assigned to this value set."
                                )
                            this_row_analysis.append(check_item)
                        else:
                            check_item={}
                            check_item=CheckItem("CHK06-OUT-NOT_FOR_PRODUCTION")
                            check_item.general_message=(
                                "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                                f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (unrecognised acceptabiliy)"
                                )
                            this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK06-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK06-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK06-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_mesage="Blank line"
            this_row_analysis.append(check_item)

    setchk_results.set_analysis["Messages"]=[] 
    
    for domain_id in domain_ids:
        domain_name=id_to_full_domain_name_dict[domain_id]
        if n_CONCEPTS_IN_DOMAIN[domain_id]!=0:
            msg=(
            f"There are {n_CONCEPTS_IN_DOMAIN[domain_id]} concepts "  
            f"that are subtypes of the {domain_name} hierarchy. " 
            )
            setchk_results.set_analysis["Messages"].append(msg)
            
    msg=(
    f"There are {n_CONCEPTS_NOT_RECOMMENDED} concepts "  
    f"in the value set that are categorised as ‘not recommended’ for the "
    f"{data_entry_extract_type} data entry type assigned to this value set."
    )
    setchk_results.set_analysis["Messages"].append(msg)
    
    msg=(
    f"There are {n_CONCEPTS_MAY_NOT_BE_APPROPRIATE} concepts "  
    f"in the value set that are categorised as ‘may not be appropriate’ for the "
    f"{data_entry_extract_type} data entry type assigned to this value set."
    )
    setchk_results.set_analysis["Messages"].append(msg)

    msg=(
        f"Your input file contains a total of {n_FILE_TOTAL_ROWS} rows.\n"
        f"The system has not assessed {n_FILE_NON_PROCESSABLE_ROWS} rows for this Set Check (blank or header rows).\n"
        f"The system has assessed {n_FILE_PROCESSABLE_ROWS} rows"
        ) 
    setchk_results.set_analysis["Messages"].append(msg)