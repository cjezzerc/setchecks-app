#!/usr/bin/env python

import sys, os, pprint

from pymongo import MongoClient

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP/')
from vsmt_uprot.terminology_server_module import TerminologyServer

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils



def download_limited_concept_data_from_ontoserver(sct_version=None, root_id=None, terminology_server=None):
    
    # relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)" % (sct_version, "<<"+str(root_id))
    relative_sub_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child" % (sct_version, "<<"+str(root_id))
    
    relative_url=relative_sub_url+"&count=0"
    response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
    print(response)
    
    temp_valueset=ValueSet.parse_obj(response.json())
    
    total_concepts=temp_valueset.expansion.total
    n_per_fetch=500
    n_fetches=int(total_concepts/n_per_fetch)
    if (total_concepts % n_per_fetch)!=0:
        n_fetches+=1

    print("Will fetch %s concepts in %s fetches" % (total_concepts, n_fetches))

    offset=0
    while offset<total_concepts:
        print("offset = %s" % (offset))
        relative_url=relative_sub_url+"&count=%s&offset=%s" % (n_per_fetch, offset)
        response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
        print(response)
        temp_valueset=ValueSet.parse_obj(response.json())
        if offset==0:
            staging_valueset=temp_valueset
        else:
            staging_valueset.expansion.contains+=temp_valueset.expansion.contains
        offset+=n_per_fetch


    # relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child&count=1" % (sct_version, "<<"+str(root_id))

    # staging_valueset.expansion.contains+=staging_valueset.expansion.contains

    # print(staging_valueset.expansion.contains)
    
    concepts={}
    
    # # print(response.json())
    # # pprint.pprint(response.json())
    # if response.json()["resourceType"]=="ValueSet": 
    #     ecl_response=[]
    #     extensional_valueset=ValueSet.parse_obj(response.json())
    #         # print(item)
    #     if extensional_valueset.expansion.contains:
    #         concepts={}
    #         for contained_item in extensional_valueset.expansion.contains:
    #             # if add_display_names:
    #             #     ecl_response.append("%20s | %s | (inactive=%s)" % (contained_item.code, contained_item.display, contained_item.inactive))
    #             # else:
    #             # print("---------------------")
    #             concept={}
    #             concept['parent']=[]
    #             concept['child']=[]
    #             concept['descendants']=set()
    #             concept['ancestors']=set()
    #             concept['display']=contained_item.display
    #             concept['code']=int(contained_item.code)
    #             for item in contained_item.extension:
    #                 property_value=None
    #                 for iv, value in enumerate([item.extension[1].valueBoolean, item.extension[1].valueString, item.extension[1].valueCode]):
    #                     if value is not None:
    #                         property_value=value
    #                 property_name=item.extension[0].valueCode
    #                 if property_name not in ['normalForm', 'normalFormTerse']:
    #                     if property_name in ['parent', 'child']:
    #                         concept[property_name].append(int(property_value))
    #                     else:
    #                         concept[property_name]=property_value
    #             concepts[concept['code']]=concept
    #             ecl_response.append((int(contained_item.code), contained_item.display)) # trial addition12 jan22         
    return concepts


terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])

releases=["20230412","20230315","20230215","20230118","20221221","20221123","20221026","20220928","20220831","20220803","20220706","20220608","20220511"]
release=releases[-1]
sct_version="http://snomed.info/sct/83821000000107/version/" + release


root_id=int(sys.argv[1])

concepts=download_limited_concept_data_from_ontoserver(sct_version=sct_version, root_id=root_id, terminology_server=terminology_server)


