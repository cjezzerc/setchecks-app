#!/usr/bin/env python

"""
This is converted from JC's personal pre NHS work
Converted to use mongodb rather than working in memory
"""

import sys
from collections import UserDict

# sys.path.append("/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_SETCHKS_APP")
# sys.path.append("/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP")
from setchks_app.concepts_service.concepts_service import ConceptsService

from pymongo import MongoClient

class Concept():

    __slots__={
        "concept_id",
        "concepts",
        "active",
        "effective_time",
        "children",
        "parents",
        "ancestors",
        "descendants",
        "pt",
        "semantic_tag",
        }
    
    # This is a minimal version using data from concepts stroed as dicts on mongodb
    # many parameters not set (including fsn)
    def __init__(self, mongo_db_concept=None, concepts=None):

        # ca=fhir_snomed_utils.parse_parameters_resource_from_snomed_concept_lookup(parameters=concept_fhir_parameters)
        self.concept_id=int(mongo_db_concept['code']) # try to avoid using bare "id" as is a built in function
        self.concepts=concepts
        # self.system=None
        # self.version=None
        # self.module_name=None
        # self.module_id=None
        self.active=not(mongo_db_concept['inactive'])
        self.effective_time=mongo_db_concept['effectiveTime']
        self.children=mongo_db_concept['child']
        self.parents=mongo_db_concept['parent']
        # self.role_groups=None
        
        # self.normal_form=None
        # self.normal_form_terse=None
        # self.ancestors="fetched_on_demand" 
        # ecl_evaluation=terminology_server.do_expand(ecl=">"+str(self.concept_id), sct_version=self.version)
        # if ecl_evaluation is not None:
        #     self.ancestors=set(ecl_evaluation)
        # else:
        #     print("WARNING: ecl_evaluation yielded None for ancestors of %s  - possible too costly error" % self.concept_id)
        #     self.ancestors=set()

        # # self.descendants="fetched on demand" 
        # ecl_evaluation=terminology_server.do_expand(ecl="<"+str(self.concept_id), sct_version=self.version)
        # if ecl_evaluation is not None:
        #     self.descendants=set(ecl_evaluation)
        # else:
        #     print("WARNING: ecl_evaluation yielded None for descendants of %s  - possible too costly error" % self.concept_id)
        #     self.descendants=set()
        self.ancestors=set(mongo_db_concept['ancestors'])
        self.descendants=set(mongo_db_concept['descendants'])

        # still need to decide best way to handle the non is-a relationships; two lines below refer back to how did it with the "all in memory" solution
        # self.modelled_relns_as_source={} # key=destination_id; value=list of type_ids
        # self.modelled_relns_as_destination={} # key=source_id; value=list of type_ids

        self.pt=mongo_db_concept['display']
        # for d in ca['designation']:
        #     if d['use']=='Fully specified name':
        #         self.fsn=d['value']
        # self.pt=ca['display']
        # mObj=re.search(r'.*\((.*?)\)$', self.fsn.strip())
        # if mObj:
        #     self.semantic_tag=mObj.groups()[0]
        # else:
        #     self.semantic_tag="NO_SEMANTIC_TAG_FOUND"
        self.semantic_tag="NO_SEMANTIC_TAGS_IN_CURRENT_MONGODB_VERSION"
    
    def __getattribute__(self, name):
        value=object.__getattribute__(self, name)
        # if value!="fetched_on_demand":  # coming back to this in June 2023 - the fetched_on_demand thing is commented out above
                                        # so value is always just returned here
        return value
        # else:
        #     print("Fetching on demand")
        #     if name=="ancestors":
        #         self.ancestors=set(terminology_server.do_expand(ecl=">"+str(self.concept_id), sct_version=self.version))
        #         return self.ancestors
        #     elif name=="descendants":
        #         self.descendants=set(terminology_server.do_expand(ecl="<"+str(self.concept_id), sct_version=self.version))
        #         return self.descendants
        #     else:
        #         print("Unexpected name to fetch")
        #         sys.exit()    
        # print(name)

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
    
    # def __init__(self, concepts_db_document=None, sct_version=None):
    def __init__(self, sct_version=None):
        cs=ConceptsService()
        self.concepts_db_document=cs.db["concepts_"+sct_version]
        self.sct_version=sct_version 
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
            # if self.sct_version is not None:
            #     concept_lookup_url="/CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&version=%s&property=*" % (key, self.sct_version)
            # else:
            #     concept_lookup_url="/CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&property=*" % (key)
            # r=self.terminology_server.do_get(relative_url=concept_lookup_url)
            # concept_fhir_parameters=Parameters.parse_obj(r.json())
            # concept=Concept(concept_fhir_parameters=concept_fhir_parameters, concepts=self, terminology_server=self.terminology_server)
        
            # print("mongo db call for concept code = %s" % key)
            mongo_db_concept=self.concepts_db_document.find_one({'code':key})
            if mongo_db_concept is not None:
                concept=Concept(mongo_db_concept=mongo_db_concept, concepts=self)
            else:
                concept=None
            self.data[key]=concept
            return self.data[key]

        # # no caching in first mongodb version
        # mongo_db_concept=self.concepts_db_document.find_one({'code':key})
        # if mongo_db_concept is not None:
        #     concept=Concept(mongo_db_concept=mongo_db_concept, concepts=self)
        # else:
        #     concept=None

        return concept




if __name__=="__main__":

    concepts=ConceptsDict(sct_version="20230510")
   
    print(concepts[91487003])
    print(concepts[91487003].ancestors)
    print(concepts[91487003])

    for parent_id in concepts[91487003].parents:
        print("PARENT: %20s : %s" % ( parent_id, concepts[parent_id].pt))

    # for role_group in concepts[91487003].role_groups:
    #     print("ROLE GROUP: ----------------")
    #     for a,b in role_group:
    #         fa=concepts[a].pt
    #         fb=concepts[b].pt
    #         print("HAS-A: %40s  : %-40s" % (fa,fb))

    print("Concepts loaded:")
    for concept_id, concept in concepts.items():
        print("%20s:%20s" % (concept_id, concept.pt))