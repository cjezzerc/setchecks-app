import os, copy, re

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict

from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.concepts_service import valid_semantic_tags

from ..check_item import CheckItem
from ..set_level_table_row import SetLevelTableRow

def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "ENTRY_PRIMARY"
        "ENTRY_OTHER"
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)
    
    ds=DescriptionsService()
    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    ##################################################################
    ##################################################################
    ##################################################################
    # Analyse membership against semantic tags                       #     
    ##################################################################
    ##################################################################
    ##################################################################
   

    tag_counts={} 
    valset_members=set()
    semantic_tags={} # will be keyed by concept_id
    for mr in setchks_session.marshalled_rows:
        if mr.C_Id is not None:
            valset_members.add(mr.C_Id)  

    for concept_id in valset_members:
        # Would be more efficient to add semantic tag into the concepts database when that is built
        # But need to get this implemented fast so calling them up on every run
        C_Id_data=ds.get_data_about_concept_id(
                concept_id=concept_id, 
                sct_version=setchks_session.sct_version,
                )
        fsn=None
        for item in C_Id_data:
            if item["term_type"]=="fsn":
                fsn=item["term"]
                break
        if fsn is not None:
            mObj=re.search(r'.*\((.*?)\)$', fsn.strip())
            if mObj:
                semantic_tag=mObj.groups()[0]
                if semantic_tag not in valid_semantic_tags.valid_semantic_tags:
                    semantic_tag="No recognisable tag" # if final parenthesis contains text other than a recognised tag  
            else:
                semantic_tag="No recognisable tag" # if there is no final parenthesis
        else:
            semantic_tag="NO_FSN_FOUND"
        semantic_tags[concept_id]=semantic_tag
        if semantic_tag not in tag_counts:
            tag_counts[semantic_tag]=0
        tag_counts[semantic_tag]+=1

    joint_majority_tag=False
    majority_tag=None
    majority_count=0
    n_concepts=0 # this will be count of distinct concepts encountered in file
    for tag, count in tag_counts.items():
        n_concepts+=count
        if count==majority_count:
            joint_majority_tag=True
        elif count>majority_count:
            joint_majority_tag=False
            majority_tag=tag
            majority_count=count
            
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
    
    for mr in setchks_session.marshalled_rows:
        n_FILE_TOTAL_ROWS+=1
        this_row_analysis=[]
        setchk_results.row_analysis.append(this_row_analysis) # when this_row_analysis is updated below, 
                                                              # this will automatically update
        if not mr.blank_row:
            concept_id=mr.C_Id
            if concept_id is not None:
                n_FILE_PROCESSABLE_ROWS+=1
                semantic_tag=semantic_tags[concept_id]
                if joint_majority_tag or semantic_tag!=majority_tag:
                    #<check_item>
                    check_item=CheckItem("CHK12-OUT-02")
                    check_item.outcome_level="ISSUE"
                    check_item.general_message=(
                        "The Semantic Tag for this Concept is not the most frequently found tag in this value set. "
                        "This may suggest it is an erroneous entry. "
                        "A full analysis of Semantic Tags used in this value set is given in the 'Set_Analysis' tab. "
                        "The Semantic Tag for this Concept is -->"
                        )
                    check_item.row_specific_message=(
                        f"{semantic_tag}"
                    )
                    this_row_analysis.append(check_item)
                    #</check_item>
                else:
                    #<check_item>
                    check_item=CheckItem("CHK12-OUT-01")
                    check_item.outcome_level="Conditional: FACT/DEBUG"
                    check_item.general_message=(
                        "The Semantic Tag for this Concept is the most frequently found tag in this value set. "
                        "The Semantic Tag for this Concept is -->"
                        )
                    check_item.row_specific_message=(
                        f"{semantic_tag}"
                        )
                    #</check_item>
                    this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                #<check_item>
                check_item=CheckItem("CHK12-OUT-NOT_FOR_PRODUCTION")
                check_item.outcome_level="ISSUE"
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS"
                    )
                #</check_item>
                this_row_analysis.append(check_item)
        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK12-OUT-03 oly applied before gatekeepr added
            #<check_item>
            check_item=CheckItem("CHK12-OUT-BLANK_ROW")
            check_item.outcome_level="DEBUG"
            check_item.general_message="Blank line"
            #</check_item>
            this_row_analysis.append(check_item)

    # assign CHK12-OUT-01 type check items depending on whether have seen mixture of tags
    # in which case useful to see what all the other tags are
    # print("======================")
    for this_row_analysis in setchk_results.row_analysis:
        for check_item in this_row_analysis:
            if check_item.outcome_code=="CHK12-OUT-01":
                if len(tag_counts)>1 and setchks_session.output_full_or_compact=="FULL_OUTPUT":
                    check_item.outcome_level="FACT"
                else:
                    check_item.outcome_level="DEBUG"

    if len(tag_counts)==1:
        #<set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[GREEN] This check has detected no issues."
                    ),
                outcome_code="CHK12-OUT-06"
                )
            )     
        #</set_level_message>
    else:
        setchk_results.set_level_table_rows.append(
            #<set_level_message>
            SetLevelTableRow(
                simple_message=(
                    "[AMBER] Your value set contains more than one type of Semantic Tag. "  
                    "This sometimes indicates that some Concepts have been erroneously included."
                    ),
                    outcome_code="CHK12-OUT-03",
                )
            )     
            #</set_level_message>
        
        
        if not joint_majority_tag:
            #<set_level_count>
            setchk_results.set_level_table_rows.append(
                SetLevelTableRow(
                    descriptor=(
                        f"Number of Concepts with the most frequently "
                        f"found Semantic Tag '({majority_tag})'" 
                        ),
                    value=f"{majority_count}", 
                    outcome_code="CHK12-OUT-04",
                    )
                )     
            #</set_level_count>

        #propose
        # tags_list= [ x for x in tag_counts].sorted()
        
        for tag, count in tag_counts.items():
            if (tag!=majority_tag) or joint_majority_tag:
                #<set_level_count>
                setchk_results.set_level_table_rows.append(
                    SetLevelTableRow(
                        descriptor=(
                            f"Number of Concepts with the Semantic Tag '({tag})'" 
                            ),
                        value=f"{count}",
                        outcome_code="CHK12-OUT-05",
                        )
                    )
                #</set_level_count>