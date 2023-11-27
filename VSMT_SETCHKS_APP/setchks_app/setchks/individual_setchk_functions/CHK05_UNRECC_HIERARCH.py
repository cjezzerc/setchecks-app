import os, copy

import logging
logger=logging.getLogger()


import setchks_app.terminology_server_module
from setchks_app.set_refactoring.concept_module import ConceptsDict



from ..check_item import CheckItem

def do_check(setchks_session=None, setchk_results=None):

    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it will only be called for data_entry_extract_types of:
        "ENTRY_PRIMARY"
        "ENTRY_OTHER"
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts=ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    ##################################################################
    ##################################################################
    ##################################################################
    # Analyse membership against the top level hierarchies           #     
    ##################################################################
    ##################################################################
    ##################################################################
   
    id_to_full_domain_name_dict={
        "123037004":"Body structure",
        "404684003":"Clinical finding",
        "308916002":"Environment or geographical location",
        "272379006":"Event",
        "363787002":"Observable entity",
        "410607006":"Organism",
        "373873005":"Pharmaceutical / biologic product",
        "78621006":"Physical force",
        "260787004":"Physical object",
        "71388002":"Procedure",
        "362981000":"Qualifier value",
        "419891008":"Record artefact",
        "243796009":"Situation with explicit context",
        "900000000000441003":"SNOMED CT Model Component",
        "48176007":"Social context",
        "370115009":"Special concept",
        "123038009":"Specimen",
        "254291000":"Staging and scales",
        "105590001":"Substance",
    }

    domain_ids=list(id_to_full_domain_name_dict.keys())

    full_domain_name_to_id_dict={}
    for k, v in id_to_full_domain_name_dict.items():
        full_domain_name_to_id_dict[v]=k

    acceptability_dicts_by_full_domain_name={}

    acceptability_dicts_by_full_domain_name["ENTRY_PRIMARY"]={
        "Body structure":"NOT_RECOMMENDED",
        "Clinical finding":"ACCEPTABLE",
        "Environment or geographical location":"NOT_RECOMMENDED",
        "Event":"ACCEPTABLE",
        "Observable entity":"NOT_RECOMMENDED",
        "Organism":"NOT_RECOMMENDED",
        "Pharmaceutical / biologic product":"MAY_NOT_BE_APPROPRIATE",
        "Physical force":"NOT_RECOMMENDED",
        "Physical object":"NOT_RECOMMENDED",
        "Procedure":"ACCEPTABLE",
        "Qualifier value":"MAY_NOT_BE_APPROPRIATE",
        "Record artefact":"NOT_RECOMMENDED",
        "Situation with explicit context":"ACCEPTABLE",
        "SNOMED CT Model Component":"NOT_RECOMMENDED",
        "Social context":"ACCEPTABLE",
        "Special concept":"NOT_RECOMMENDED",
        "Specimen":"NOT_RECOMMENDED",
        "Staging and scales":"NOT_RECOMMENDED",
        "Substance":"ACCEPTABLE",    
    }

    acceptability_dicts_by_full_domain_name["ENTRY_OTHER"]=copy.deepcopy(acceptability_dicts_by_full_domain_name["ENTRY_PRIMARY"])
    acceptability_dicts_by_full_domain_name["ENTRY_OTHER"]["Pharmaceutical / biologic product"]="ACCEPTABLE"
    acceptability_dicts_by_full_domain_name["ENTRY_OTHER"]["Qualifier value"]="ACCEPTABLE"

    acceptability_dicts_by_id={}
    for data_entry_extract_type in ["ENTRY_PRIMARY", "ENTRY_OTHER"]:
        acceptability_dicts_by_id[data_entry_extract_type]={}
        for name, acceptability in acceptability_dicts_by_full_domain_name[data_entry_extract_type].items():
            acceptability_dicts_by_id[data_entry_extract_type][full_domain_name_to_id_dict[name]]=acceptability

    valset_members_in_domain_dict={} # will be keyed by domain id
                                  # value will be the set of ids from the value set that are in the domain
    valset_members=set()
    for mr in setchks_session.marshalled_rows:
        if mr.C_Id is not None:
            valset_members.add(mr.C_Id)  
    print(f"valset_members {valset_members}")
    for domain_id in domain_ids:
        domain_members=set(str(x) for x in concepts[domain_id].descendants)  # really need this done upstream!!!!
                                                                            # concepts service seems to be working in ints
        print(domain_id, len(domain_members),list(domain_members)[:3])
        valset_members_in_domain_dict[domain_id]=valset_members.intersection(domain_members)
    print(f"valset_members_in_domain_dict {valset_members_in_domain_dict}")

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
                        elif acceptability=="MAY_NOT_BE_APPROPRIATE": 
                            n_CONCEPTS_MAY_NOT_BE_APPROPRIATE+=1
                            check_item=CheckItem("CHK05-OUT-03")
                            check_item.general_message=(
                                f"The Concept Id is a subtype of the {domain_name} hierarchy in SNOMED CT." 
                                f"The hierarchy has been categorised as ‘may not be appropriate’ for the "
                                f"{data_entry_extract_type} data entry type assigned to this value set."
                                )
                            this_row_analysis.append(check_item)
                        elif acceptability=="NOT_RECOMMENDED": 
                            n_CONCEPTS_NOT_RECOMMENDED+=1
                            check_item=CheckItem("CHK05-OUT-04")
                            check_item.general_message=(
                                f"The Concept Id is a subtype of the {domain_name} hierarchy in SNOMED CT." 
                                f"The hierarchy has been categorised as ‘not recommended’ for the "
                                f"{data_entry_extract_type} data entry type assigned to this value set."
                                )
                            this_row_analysis.append(check_item)
                        else:
                            check_item={}
                            check_item=CheckItem("CHK05-OUT-NOT_FOR_PRODUCTION")
                            check_item.general_message=(
                                "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                                f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (unrecognised acceptabiliy)"
                                )
                            this_row_analysis.append(check_item)
            else:
                # gatekeeper should catch this. This clause allows code to run without gatekeeper
                check_item={}
                check_item=CheckItem("CHK05-OUT-NOT_FOR_PRODUCTION")
                check_item.general_message=(
                    "THIS RESULT SHOULD NOT OCCUR IN PRODUCTION: "
                    f"PLEASE REPORT TO THE SOFTWARE DEVELOPERS (mr.C_Id is None)"
                    )
                this_row_analysis.append(check_item)

        else:
            n_FILE_NON_PROCESSABLE_ROWS+=1 # These are blank rows; no message needed NB CHK05-OUT-03 oly applied before gatekeepr added
            check_item=CheckItem("CHK05-OUT-BLANK_ROW")
            check_item.outcome_level="INFO"
            check_item.general_message="Blank line"
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