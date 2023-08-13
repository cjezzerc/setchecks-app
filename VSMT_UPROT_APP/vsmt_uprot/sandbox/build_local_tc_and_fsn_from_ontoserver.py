#!/usr/bin/env python

import sys, os, pprint

from pymongo import MongoClient

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP/')
from vsmt_uprot.terminology_server_module import TerminologyServer

from fhir.resources.valueset import ValueSet
import vsmt_uprot.fhir_utils

def transitive_closure(start_id, concepts, visited): # at first call pass in visited as empty dictionary 
    # This version used dictionary form for concept as quick preliminary implementation
    #
    # This is a straightforward translation of the perl script provided by IHTSDO
    # global counter
    # counter+=1
    # if counter%1000==0:
    #     print("Visit", start_id,counter)

    for child_id in concepts[start_id]['child']:                    # for all the children of the startnode
        if child_id not in visited:                                 # if it has not already been traversed
            transitive_closure(child_id, concepts, visited)         # recursively visit the childnode
            visited[child_id]=True                                  # and when the recursive visit completes, mark as visited
        for descendant_id in concepts[child_id]['descendants']:        # for each descendant of childnode
            concepts[start_id]['descendants'].add(descendant_id)        # mark as a descendant of startnode
            concepts[descendant_id]['ancestors'].add(start_id)          # and ditto m.m. for ancestor
        concepts[start_id]['descendants'].add(child_id)                 # mark the immediate childnode as a descendant of startnode
        concepts[child_id]['ancestors'].add(start_id)                   # and ditto m.m. for ancestor

    # for child_id in concepts[start_id].children:                    # for all the children of the startnode
    #     if child_id not in visited:                                 # if it has not already been traversed
    #         transitive_closure(child_id, concepts, visited)         # recursively visit the childnode
    #         visited[child_id]=True                                  # and when the recursive visit completes, mark as visited
    #     for descendant_id in concepts[child_id].descendants:        # for each descendant of childnode
    #         concepts[start_id].add_descendant(descendant_id, tolerate_adding_again=True)        # mark as a descendant of startnode
    #         concepts[descendant_id].add_ancestor(start_id, tolerate_adding_again=True)          # and ditto m.m. for ancestor
    #     concepts[start_id].add_descendant(child_id, tolerate_adding_again=True)                 # mark the immediate childnode as a descendant of startnode
    #     concepts[child_id].add_ancestor(start_id, tolerate_adding_again=True)                   # and ditto m.m. for ancestor

def download_limited_concept_data_from_ontoserver(sct_version=None, root_id=None):
    
    # relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)" % (sct_version, "<<"+str(root_id))
    # relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child" % (sct_version, "<<"+str(root_id))
    
    # response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
    # print(response)


    concepts={}

    
    relative_sub_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child" % (sct_version, "<<"+str(root_id))
    
    relative_url=relative_sub_url+"&count=0"
    
    
    terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])
    response=terminology_server.do_get(relative_url=relative_url, verbose=True) 

    temp_valueset=ValueSet.parse_obj(response.json())
    total_concepts=temp_valueset.expansion.total
    n_per_fetch=1000
    n_fetches=int(total_concepts/n_per_fetch)
    if (total_concepts % n_per_fetch)!=0:
        n_fetches+=1
    print("Will fetch %s concepts in %s fetches" % (total_concepts, n_fetches))
    offset=0
    while offset<total_concepts:
        print("offset = %s" % (offset))
        relative_url=relative_sub_url+"&count=%s&offset=%s" % (n_per_fetch, offset)
        terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"]) # call every time as bodge to prevent token expiring
        response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
        print(response)
        print("Parsing..")
        temp_valueset=ValueSet.parse_obj(response.json())
        # if offset==0:
        #     staging_valueset=temp_valueset
        # else:
        #     staging_valueset.expansion.contains+=temp_valueset.expansion.contains


    # if response.json()["resourceType"]=="ValueSet": 
    #     ecl_response=[]
    #     staging_valueset=ValueSet.parse_obj(response.json())
            # print(item)
    # if staging_valueset.expansion.contains:
    #     concepts={}
        for contained_item in temp_valueset.expansion.contains:
            # if add_display_names:
            #     ecl_response.append("%20s | %s | (inactive=%s)" % (contained_item.code, contained_item.display, contained_item.inactive))
            # else:
            # print("---------------------")
            concept={}
            concept['parent']=[]
            concept['child']=[]
            concept['descendants']=set()
            concept['ancestors']=set()
            concept['display']=contained_item.display
            concept['code']=int(contained_item.code)
            for item in contained_item.extension:
                property_value=None
                for iv, value in enumerate([item.extension[1].valueBoolean, item.extension[1].valueString, item.extension[1].valueCode]):
                    if value is not None:
                        property_value=value
                property_name=item.extension[0].valueCode
                if property_name not in ['normalForm', 'normalFormTerse']:
                    if property_name in ['parent', 'child']:
                        concept[property_name].append(int(property_value))
                    else:
                        concept[property_name]=property_value
            concepts[concept['code']]=concept
            # ecl_response.append((int(contained_item.code), contained_item.display)) # trial addition12 jan22         
        offset+=n_per_fetch

    return concepts

def add_concept_to_db(concept=None, db_document=None):
    print("Adding %s to db" % concept['code'])
    db_document.insert_one(concept)

# terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
#                                      auth_url=os.environ["ONTOAUTH_INSTANCE"])

releases=["20230412","20230315","20230215","20230118","20221221","20221123","20221026","20220928","20220831","20220803","20220706","20220608","20220511"]
release=releases[-1]
sct_version="http://snomed.info/sct/83821000000107/version/" + release
# root_id=25899002
# root_id=125605004
# root_id=116312005
# 116312005 is a good big example (7000 descendants)
# 25899002 is a good small example (about 7 descendants)

root_id=int(sys.argv[1])

concepts=download_limited_concept_data_from_ontoserver(sct_version=sct_version, root_id=root_id)
# pprint.pprint(concepts)
# print(len(concepts.keys()))

transitive_closure(root_id, concepts, {})

for code, concept in concepts.items():
    concept['ancestors']=list(concept['ancestors'])
    concept['descendants']=list(concept['descendants'])
# pprint.pprint(concepts)


client=MongoClient()
db=client['VSMT_uprot_app']
db_document=db['concepts']

for code, concept in concepts.items():
    add_concept_to_db(concept=concept, db_document=db_document)
