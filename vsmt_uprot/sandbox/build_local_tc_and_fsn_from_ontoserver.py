#!/usr/bin/env python

import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/')
from vsmt_uprot.terminology_server_module import TerminologyServer

from fhir.resources.valueset import ValueSet

def transitive_closure(start_id, concepts, visited): # at first call pass in visited as empty dictionary 
    # This is a straightforward translation of the perl script provided by IHTSDO
    # global counter
    # counter+=1
    # if counter%1000==0:
    #     print("Visit", start_id,counter)

    for child_id in concepts[start_id].children:                    # for all the children of the startnode
        if child_id not in visited:                                 # if it has not already been traversed
            transitive_closure(child_id, concepts, visited)         # recursively visit the childnode
            visited[child_id]=True                                  # and when the recursive visit completes, mark as visited
        for descendant_id in concepts[child_id].descendants:        # for each descendant of childnode
            concepts[start_id].add_descendant(descendant_id, tolerate_adding_again=True)        # mark as a descendant of startnode
            concepts[descendant_id].add_ancestor(start_id, tolerate_adding_again=True)          # and ditto m.m. for ancestor
        concepts[start_id].add_descendant(child_id, tolerate_adding_again=True)                 # mark the immediate childnode as a descendant of startnode
        concepts[child_id].add_ancestor(start_id, tolerate_adding_again=True)                   # and ditto m.m. for ancestor

def download_limited_concept_data_from_ontoserver(sct_version=None, root_id=None, terminology_server=None):
    
    relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)" % (sct_version, "<<"+str(root_id))
    
    response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
    print(response)
    # print(response.json())
    if response.json()["resourceType"]=="ValueSet": 
        ecl_response=[]
        extensional_valueset=ValueSet.parse_obj(response.json())
        if extensional_valueset.expansion.contains:
            for contained_item in extensional_valueset.expansion.contains:
                # if add_display_names:
                #     ecl_response.append("%20s | %s | (inactive=%s)" % (contained_item.code, contained_item.display, contained_item.inactive))
                # else:
                ecl_response.append(int(contained_item.code)) # trial addition12 jan22         
    return ecl_response

terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])

releases=["20230412","20230315","20230215","20230118","20221221","20221123","20221026","20220928","20220831","20220803","20220706","20220608","20220511"]
release=releases[-1]
sct_version="http://snomed.info/sct/83821000000107/version/" + release
# root_id=25899002
root_id=125605004
root_id=int(sys.argv[1])

concepts=download_limited_concept_data_from_ontoserver(sct_version=sct_version, root_id=root_id, terminology_server=terminology_server)
print(concepts)
print(len(concepts))
