#!/usr/bin/env python

import re, time
from collections import UserDict
import requests

from fhir.resources.parameters import Parameters
from fhir.resources.valueset import ValueSet
import fhir_utils
import fhir_snomed_utils
import terminology_server_module

class Concept():
    def __init__(self, *, concept_fhir_parameters, concepts, terminology_server):
        if concept_fhir_parameters:

            ca=fhir_snomed_utils.parse_parameters_resource_from_snomed_concept_lookup(parameters=concept_fhir_parameters)
            self.concept_id=int(ca['code']) # try to avoid using bare "id" as is a built in function
            self.concepts=concepts
            self.system=ca['system']
            self.version=ca['version']
            self.module_name=ca['name']   # need to check this?
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
            
            self.normal_form=ca.get('normalForm','N/A') # ? not available if inactive?
            self.normal_form_terse=ca.get('normalFormTerse','N/A')
            # self.ancestors="fetched_on_demand" 
            ecl_evaluation=terminology_server.do_expand(ecl=">"+str(self.concept_id), sct_version=self.version)
            if ecl_evaluation is not None:
                self.ancestors=set(ecl_evaluation)
            else:
                print("WARNING: ecl_evaluation yielded None for ancestors of %s  - possible too costly error" % self.concept_id)
                self.ancestors=set()

            # self.descendants="fetched on demand" 
            ecl_evaluation=terminology_server.do_expand(ecl="<"+str(self.concept_id), sct_version=self.version)
            if ecl_evaluation is not None:
                self.descendants=set(ecl_evaluation)
            else:
                print("WARNING: ecl_evaluation yielded None for descendants of %s  - possible too costly error" % self.concept_id)
                self.descendants=set()

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
        if value!="fetched_on_demand":  # coming back to this in June 2023 - the fetched_on_demand thing is commented out above
                                        # so value is always just returned here
            return value
        else:
            print("Fetching on demand")
            if name=="ancestors":
                self.ancestors=set(terminology_server.do_expand(ecl=">"+str(self.concept_id), sct_version=self.version))
                return self.ancestors
            elif name=="descendants":
                self.descendants=set(terminology_server.do_expand(ecl="<"+str(self.concept_id), sct_version=self.version))
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
                    repr_strings.append("%20s : %s (%s)" % (k,v,type(v)))
        return "\n".join(repr_strings)

class ConceptsDict(UserDict):
    
    def __init__(self, terminology_server=None, sct_version=None):
        self.terminology_server=terminology_server
        self.sct_version=sct_version  # really should protect against changing this and not clearing out all old data
        super().__init__()

    def __getitem__(self, key):
        if type(key)==str:
            key=int(key)
        verbose=False
        
        # print("Current_keys_in_ConceptsDict:", self.data.keys())

        if verbose:
            print("=======================")
            print("Requested key: %s (%s)" % (key,type(key)))
            print("Current keys:", self.data.keys())

        if key in self.data: # if have already fetched this concept
            if verbose:
                print("Already have this key")
            return self.data[key]
        else: # otherwise need to fetch it
            if verbose:
                print("Need to fetch this key")
                print("=======================")
            if self.sct_version is not None:
                concept_lookup_url="/CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&version=%s&property=*" % (key, self.sct_version)
            else:
                concept_lookup_url="/CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&property=*" % (key)
            r=self.terminology_server.do_get(relative_url=concept_lookup_url)
            concept_fhir_parameters=Parameters.parse_obj(r.json())
            concept=Concept(concept_fhir_parameters=concept_fhir_parameters, concepts=self, terminology_server=self.terminology_server)
            self.data[key]=concept
            return self.data[key]

if __name__=="__main__":

    terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    concepts=ConceptsDict(terminology_server=terminology_server, sct_version="http://snomed.info/sct/83821000000107/version/20190807")
   
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