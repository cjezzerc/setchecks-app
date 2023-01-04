#!/usr/bin/env python

import re, time
from collections import UserDict
import requests

from fhir.resources.parameters import Parameters
from fhir.resources.valueset import ValueSet
import fhir_utils
import fhir_snomed_utils
import terminology_server

class Concept():
    def __init__(self,concept_fhir_parameters=None, concepts=None):
        if concept_fhir_parameters:

            ca=fhir_snomed_utils.parse_parameters_resource_from_snomed_concept_lookup(parameters=concept_fhir_parameters)
            # print("\n".join(list(ca.keys())))
            
            self.concept_id=ca['code'] # try to avoid using bare "id" as is a built in function
            self.concepts=concepts
            self.system=ca['system']
            self.version=ca['version']
            self.module_name=ca['name']
            self.module_id=ca['moduleId']
            self.active=not(ca['inactive'])
            self.effective_time=ca['effectiveTime']
            if 'child' in ca:
                self.children=ca['child']
            else:
                self.children=[]
            if 'parent' in ca:
                self.parents=ca['parent']
            else:
                self.parents=[]
            if '609096000' in ca:
                self.role_groups=ca['609096000']
            else:
                self.role_groups=[]
            self.normal_form=ca['normalForm']
            self.normal_form_terse=ca['normalFormTerse']
            self.ancestors="fetched_on_demand" 
            self.descendants="fetched on demand" 
            # still need to decide best way to handle the non is-a relationships; two lines below refer back to how did it with the "all in memory" solution
            # self.modelled_relns_as_source={} # key=destination_id; value=list of type_ids
            # self.modelled_relns_as_destination={} # key=source_id; value=list of type_ids
            for d in ca['designation']:
                if d['use']=='Fully specified name':
                    self.fsn=d['value']
            self.pt=ca['display']
            mObj=re.search(r'.*\((.*?)\)$', self.fsn.strip())
            if mObj:
                self.semantic_tag=mObj.groups()[0]
            else:
                self.semantic_tag="NO_SEMANTIC_TAG_FOUND"
    
    def __getattribute__(self, name):
        value=object.__getattribute__(self, name)
        if value!="fetched_on_demand":
            return value
        else:
            print("Fetching on demand")
            if name=="ancestors":
                self.ancestors=set(terminology_server.expand_ecl(ecl=">"+str(self.concept_id), version=self.version))
                return self.ancestors
            elif name=="descendants":
                self.descendants=set(terminology_server.expand_ecl(ecl="<"+str(self.concept_id), version=self.version))
                return self.descendants
            else:
                print("Unexpected name to fetch")
                sys.exit()    
        print(name)

    def __repr__(self):
        repr_strings=[]
        for k,v in self.__dict__.items():
            if k not in ["concepts", "normal_form","normal_form_terse"]:
                if type(v) in (list, set) and len(v)>20:
                    repr_strings.append("%20s : %s of %s elements" % (k, type(v), len(v)))
                else:
                    repr_strings.append("%20s : %s" % (k,v))
        return "\n".join(repr_strings)

class ConceptsDict(UserDict):
    def __init__(self):
        self.url_format="https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&version=http://snomed.info/sct/83821000000107/version/20190807&property=*"
        super().__init__()
    def __getitem__(self, key):
        # print("Handling", key)
        if key in self.data: # if have already fetched this concept
            return self.data[key]
        else: # otherwise need to fetch it
            r=terminology_server.do_get(url=self.url_format % key)
            concept_fhir_parameters=Parameters.parse_obj(r.json())
            concept=Concept(concept_fhir_parameters=concept_fhir_parameters, concepts=self)
            self.data[key]=concept
            return self.data[key]

if __name__=="__main__":
    concepts=ConceptsDict()
   
    print(concepts[91487003])
    print(concepts[91487003].ancestors)
    print(concepts[91487003])

    for parent_id in concepts[91487003].parents:
        print("PARENT: %20s : %s" % ( parent_id, concepts[parent_id].fsn))

    for role_group in concepts[91487003].role_groups:
        print("ROLE GROUP: ----------------")
        for a,b in role_group:
            fa=concepts[a].pt
            fb=concepts[b].pt
            print("HAS-A: %40s  : %-40s" % (fa,fb))

    print("Concepts loaded:")
    for concept_id, concept in concepts.items():
        print("%20s:%20s" % (concept_id, concept.fsn))