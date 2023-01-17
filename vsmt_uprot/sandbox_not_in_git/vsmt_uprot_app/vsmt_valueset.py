#!/usr/bin/env python

import sys, json, random, datetime

import requests
import sys

from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeFilter, ValueSetComposeIncludeConcept
from fhir.resources.extension import Extension
from fhir.resources.bundle import Bundle
from fhir.resources.identifier import Identifier

import vsmt_uprot.fhir_utils
import vsmt_uprot.terminology_server_module

####################################################################
# Classes to get info about all available VSMT_ValueSets on server #
####################################################################

class VSMT_ValueSetManager():

    def __init__(self, terminology_server=None):
        self.terminology_server=terminology_server

    def get_vsmt_index_data(self):
        relative_url="ValueSet?_elements=id,title,version,identifier&publisher:contains=VSMT-prototyping"
        vsmt_index_response=self.terminology_server.do_get(relative_url=relative_url)
        vsmt_index_dict=vsmt_index_response.json()
        vsmt_index={}
        for entry in vsmt_index_dict['entry']:
            resource_dict=entry['resource']
            index_item=VSMT_IndexItem(vsmt_version=resource_dict["version"], 
                                    vsmt_identifier=resource_dict["identifier"][0]["value"],
                                    vsmt_human_name=resource_dict["title"],
                                    server_id=resource_dict["id"],
                                    server_vsn=resource_dict["meta"]['versionId'],
                                    )
            if index_item.identifier_and_version in vsmt_index:
                print("FATAL ERROR: The key %s has already been seen in the index" % index_item.identifier_and_version)
                sys.exit()
            else:
                vsmt_index[index_item.identifier_and_version]=index_item
        return vsmt_index

class VSMT_IndexItem():

    def __init__(self, vsmt_version=None, vsmt_identifier=None, vsmt_human_name=None, server_id=None, server_vsn=None):
        self.vsmt_version=vsmt_version
        self.vsmt_identifier=vsmt_identifier
        self.vsmt_human_name=vsmt_human_name
        self.server_id=server_id
        self.server_vsn=server_vsn
        self.identifier_and_version=self.vsmt_identifier+":"+self.vsmt_version

    def __repr__(self):
        return "VSMT_identifier: %5s | vsn: %3s | server_id: %32s | server_vsn: %3s | name: %s" % (self.vsmt_identifier, 
                                                                                            self.vsmt_version,
                                                                                            self.server_id,
                                                                                            self.server_vsn, 
                                                                                            self.vsmt_human_name,)

##########################
# VSMT_VersionedValueSet #
##########################

class VSMT_VersionedValueSet():
    def __init__(self, terminology_server=None, vsmt_identifier_and_version=None, server_id=None, title=None, save_to_server=True):
        # if (server_id and title) or (not (server_id or title)): # must specify ONLY ONE of server_id or title
        #                                                         # if title specified then will create new value set on server??
        #     self=None
        one_and_only_one_defined=sum([int(bool(x not in ["", None])) for x in [vsmt_identifier_and_version, server_id, title]])==1
        if not one_and_only_one_defined:
            print("FATAL ERROR: Require one and only one of vsmt_identifier, server_id or title to be defined in VSMT_VersionedValueSet __init__")
            sys.exit()

        if server_id or vsmt_identifier_and_version: # retrieve fhir_valueset from server and initialise a VSMT_VersionValueSet to hold it
            self.terminology_server=terminology_server
            
            if vsmt_identifier_and_version:
                relative_url='/ValueSet/%s' % VSMT_ValueSetManager(terminology_server=terminology_server).get_vsmt_index_data()[vsmt_identifier_and_version].server_id
            else:
                relative_url='/ValueSet/%s' % server_id
            response=terminology_server.do_get(relative_url=relative_url)
            valueset_json_as_dict=response.json()
            self.fhir_valueset=ValueSet.parse_obj(valueset_json_as_dict)

        if title: # create a new empty ValueSet and initialise a VSMT_VersionValueSet to hold it, and store to server
            self.terminology_server=terminology_server
            ###################################################################
            # Quick and dirty method to find next VSMT_???? identifier to use #
            #                                                                 #
            value_set_manager=VSMT_ValueSetManager(terminology_server=terminology_server)
            vsmt_index=value_set_manager.get_vsmt_index_data()
            used_identifiers=[int(vii.vsmt_identifier.split("_")[1]) for vii in vsmt_index.values()]
            print(used_identifiers)
            vsmt_identifier="VSMT_"+str(sorted(used_identifiers)[-1]+1)
            vsmt_version=0
            print("New identifier:", vsmt_identifier)
            #                                                                 #
            ###################################################################
            
            self.fhir_valueset=ValueSet(title=title,                                        
                                        publisher='VSMT-prototyping', status='draft', 
                                        identifier=[Identifier(value=vsmt_identifier)], 
                                        version=vsmt_version,
                                        url='http:vsmt_prototyping/'+vsmt_identifier+'/'+str(vsmt_version)
                                        )
            if save_to_server: # only override this to avoid proliferation of test valuesets that do not want to save to server
                self.store_to_server()
            
    def get_vsmt_identifier(self):
        try:
            return self.fhir_valueset.identifier[0].value
        except:
            return None

    def set_new_vsmt_version(self, *, new_vsmt_version, save_to_server=True): # this routine leaves it to the caller to decide a sensible new version string 
        self.fhir_valueset.version=new_vsmt_version
        self.fhir_valueset.id=None # force server to store new version with new server_id
        if save_to_server: # only override this to avoid proliferation of test valuesets that do not want to save to server
            self.store_to_server()
        
    def get_vsmt_version(self):
        try:
            return self.fhir_valueset.version
        except:
            return None

    def get_vsmt_identifier_and_version(self):
        if self.get_vsmt_identifier() and self.get_vsmt_version():
            return(self.get_vsmt_identifier()+":"+self.get_vsmt_version())
        else:
            return None

    def get_vsmt_human_name(self):
        return self.fhir_valueset.title

    def store_to_server(self, verbose=False):
        if self.fhir_valueset.id==None:  
            relative_url="/ValueSet" 
            response=self.terminology_server.do_post(relative_url, json=json.loads(self.fhir_valueset.json()), verbose=verbose) # POST first time
        else:
            relative_url="/ValueSet/%s" % self.fhir_valueset.id
            response=self.terminology_server.do_put(relative_url, json=json.loads(self.fhir_valueset.json()), verbose=verbose) # PUT to update  
        # print(response.json())
        self.fhir_valueset=ValueSet.parse_obj(response.json()) # reparse object to fill out id (if not already set) and update time and server version
        return(response)

    def add_include(self, *, ecl_filter):
        self.add_include_or_exclude(clude_type="include", ecl_filter=ecl_filter)

    def add_exclude(self, *, ecl_filter):
        self.add_include_or_exclude(clude_type="exclude", ecl_filter=ecl_filter)
     
    def add_include_or_exclude(self, *, clude_type, ecl_filter):
        if self.fhir_valueset.compose==None: 
            self.fhir_valueset.compose=ValueSetCompose(include=[], exclude=[]) 
        # clude=self.fhir_valueset.compose.__dict__[clude_type]  ## WARNING !! This does not work; seems to point to different object
        if self.fhir_valueset.compose.__dict__[clude_type] is None: # ?? sending vs to server with exlude=[] sends it back as exclude=None ??
            self.fhir_valueset.compose.__dict__[clude_type]=[]
        if type(ecl_filter) == list:
            filter_list=[]
            for sub_filter in ecl_filter:
                filter_list.append(ValueSetComposeIncludeFilter(property='constraint', op='=', value=sub_filter))
        else: 
            filter_list=[ValueSetComposeIncludeFilter(property='constraint', op='=', value=ecl_filter)]
        self.fhir_valueset.compose.__dict__[clude_type].append(ValueSetComposeInclude(system='http://snomed.info/sct',
                                                    filter=filter_list))

    def delete_include(self, *, element_to_delete):
        self.delete_include_or_exclude(clude_type="include", element_to_delete=element_to_delete)

    def delete_exclude(self, *, element_to_delete):
        self.delete_include_or_exclude(clude_type="exclude", element_to_delete=element_to_delete)

    def delete_include_or_exclude(self, *, clude_type, element_to_delete):
        if self.fhir_valueset.compose==None: 
            self.fhir_valueset.compose=ValueSetCompose(include=[], exclude=[]) 
        if self.fhir_valueset.compose.__dict__[clude_type] is None: # ?? sending vs to server with exlude=[] sends it back as exclude=None ??
            self.fhir_valueset.compose.__dict__[clude_type]=[]
        if len(self.fhir_valueset.compose.__dict__[clude_type])>element_to_delete:
            del self.fhir_valueset.compose.__dict__[clude_type][element_to_delete]

    def get_includes(self):
        return self.get_includes_or_excludes(clude_type="include")

    def get_excludes(self):
        return self.get_includes_or_excludes(clude_type="exclude")

    def get_includes_or_excludes(self, *, clude_type):
        if self.fhir_valueset.compose==None:
            self.fhir_valueset.compose=ValueSetCompose(include=[], exclude=[]) 
        cludes=[]
        if self.fhir_valueset.compose.__dict__[clude_type] is not None: #fhir.resource stores empty exclude list as None 
            for clude in self.fhir_valueset.compose.__dict__[clude_type]: # clude_type is either include or exclude
                filters=[]
                for filter in clude.filter:
                    # print(filter)
                    filters.append(filter.value)
                cludes.append(filters)
        return cludes

    
    

    def set_inactive_flag(self, *, inactive): # this appears only to be safe once sure have a compose statement with one include in it
                                              # otherwise server will compain when try to store it
                                              # Perhaps should add some tests to store_on_server 
        if self.fhir_valueset.compose==None:
            print("ERROR: Cannot set compose,inactive until have a compose with at least one include statement in it, or server complains")
            sys.exit()
        self.fhir_valueset.compose.inactive=inactive

    def expand_version_on_server(self, add_display_names=False, sct_version=None):
        # return self.terminology_server.expand_value_set(value_set_server_id=self.fhir_valueset.id)
        return self.terminology_server.do_expand(value_set_server_id=self.fhir_valueset.id, add_display_names=add_display_names, sct_version=sct_version)

    def __str__(self):
        return "\n".join(fhir_utils.repr_resource(self.fhir_valueset))

####################################
# code checking during deveeloment #
####################################

if __name__=="__main__":

    terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    
    ### get basic index data on all VSMT value sets on server
    value_set_manager=VSMT_ValueSetManager(terminology_server=terminology_server)
    vsmt_index=value_set_manager.get_vsmt_index_data()
    
    for k, v in vsmt_index.items():
        print("%15s - %s" % (k,v))

    ### fetch an existing value set
    # server_id=vsmt_index['VSMT_1000:3'].server_id
    # vs=VSMT_VersionedValueSet(terminology_server=terminology_server, server_id=server_id)
    # print(vs)
    # ## vs.fhir_valueset.compose.include[0].concept=[ValueSetComposeIncludeConcept(code='12121212121')]  fhir.resources lets us add a concept cluase when a filter already exists
    # print("VSMT_identifier: %s VSMT_version: %s" % (vs.get_vsmt_identifier(), vs.get_vsmt_version()))

    ## Make a new value set and store
    # vs=VSMT_VersionedValueSet(title='cjc_test123', terminology_server=terminology_server, save_to_server=False)
    # vs.add_include(ecl_filter='<<123456')
    # print(vs)
    # print(vs.fhir_valueset.compose.include[0].valueSet)
    # print(vs.fhir_valueset.compose.include[0])
    # server_id=vsmt_index['VSMT_1003:0'].server_id
    # vs=VSMT_VersionedValueSet(terminology_server=terminology_server, server_id=server_id)

    # add a filter to a vs
    # vs=VSMT_VersionedValueSet(title='cjc_amnio_test1', terminology_server=terminology_server)
    # vs.add_include(ecl_filter='<366335008')
    # vs.add_include(ecl_filter='<408780005')
    # vs.add_exclude(ecl_filter='<<408792005')
    # vs.add_exclude(ecl_filter='<<408793000')
    # vs.add_exclude(ecl_filter='<<408794006')
    # vs.store_to_server()
    # print(vs)

    # vsmt_identifier_and_version='VSMT_1005:0'
    # print("VSMT identifier and version -", vsmt_identifier_and_version)
    # vs=VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=vsmt_identifier_and_version)
    # vs.add_include(ecl_filter=['HELLO IN','ALSO IN'])
    # vs.add_exclude(ecl_filter='HELLO OUT')
    # print(vs.get_includes())
    # print(vs.get_excludes())
    # vs.delete_include(element_to_delete=3)
    # vs.delete_exclude(element_to_delete=0)
    # print(vs.get_includes())
    # print(vs.get_excludes())
    # vs.store_to_server()
    # print(vs)

    vsmt_identifier_and_version='VSMT_1005:0'
    vs=VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=vsmt_identifier_and_version)
    print(vs.server_id)
    vs.add.exclude(ecl_filter='<<1111111111111')
    vs.set_new_vsmt_version(vsmt_version=1)
    print(vs.server_id)

    # print(vs)
    # for concept in vs.expand_version_on_server(add_display_names=True, sct_version="http://snomed.info/sct/83821000000107/version/20190807"):
    # # for concept in vs.expand_version_on_server(add_display_names=True):
    #     print(concept)

    # n_expansion1=len(vs.expand_version_on_server(add_display_names=True, sct_version="http://snomed.info/sct/83821000000107/version/20190807"))
    # n_expansion2=len(vs.expand_version_on_server(add_display_names=True, sct_version="http://snomed.info/sct/83821000000107/version/20200415"))
    # n_expansion2=len(vs.expand_version_on_server(add_display_names=True, sct_version="http://snomed.info/sct/83821000000107/version/20201223"))
    # n_expansion2=len(vs.expand_version_on_server(add_display_names=True, sct_version="http://snomed.info/sct/32506021000036107/version/20220930")) # AU


    # make "energy and stmina finding including inactives" value set
    # vs=VSMT_VersionedValueSet(title='cjc_energy_and_stamina_finding_including_inactives', terminology_server=terminology_server)
    # vs.add_include(ecl_filter='<359752005')
    # vs.set_inactive_flag(inactive=True)
    # vs.store_to_server()
    # print(vs)
    # sys.exit()

    # ###################################################################################
    # # expand "energy and stamina finding" value set against two releases and compare
    # ###################################################################################
    # from concept_module import ConceptsDict
    # vsmt_identifier_and_version='VSMT_1005:0'
    # print("VSMT identifier and version -", vsmt_identifier_and_version)
    # vs=VSMT_VersionedValueSet(terminology_server=terminology_server, vsmt_identifier_and_version=vsmt_identifier_and_version)
    # print(vs)
    # # vs.set_inactive_flag(inactive=False)
    # # vs.add_include(ecl_filter="272062008")
    # # vs.add_include(ecl_filter="<123456789")
    # # vs.store_to_server()

    # sct_version1="http://snomed.info/sct/83821000000107/version/" + "20200415"
    # expansion1=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version1)
    # sct_concepts1=ConceptsDict(terminology_server=terminology_server, sct_version=sct_version1)
    # print(len(expansion1))
    # sct_version2="http://snomed.info/sct/83821000000107/version/" + "20200805"

    # expansion2=vs.expand_version_on_server(add_display_names=True, sct_version=sct_version2)
    # sct_concepts2=ConceptsDict(terminology_server=terminology_server, sct_version=sct_version2)
    # print(len(expansion2))
    # print("==========================")

    # print(sct_concepts1[272060000])
    # print("==========================")

    # print(sct_concepts2[272060000])
    # # for stuff in expansion1:
    # #     concept_id=int(stuff.split("|")[0])
    # #     print(sct_concepts1[concept_id])

    # print("==========================")

    # for concept in expansion1:
    #     if concept not in expansion2:
    #         concept_id=int(concept.split("|")[0])
    #         print(concept, sct_concepts1[concept_id].active, sct_concepts2[concept_id].active)

    # print("==========================")

    # for concept in expansion2:
    #     if concept not in expansion1:
    #         print(concept)

    # print("==========================")

    ##################################################################################


    # https://r4.ontoserver.csiro.au/fhir/ValueSet/451fd69c-8726-46c5-bb82-4c620eff4920/$expand?system-version=http://snomed.info/sct%7Chttp://snomed.info/sct/83821000000107/version/20190807

    # from concept_module import ConceptsDict
    # concepts=ConceptsDict(terminology_server=terminology_server, sct_version="http://snomed.info/sct/83821000000107/version/20190807")
    # print(concepts[91487003])
    # for concept in vs.expand_version_on_server():
    #     print(concept)
    #     print(concepts[concept])


    # action = "Added code " + str(random.randint(1000000000000, 3000000000000))
    # datestamp=str(datetime.datetime.now())
    # vs.fhir_valueset.compose.include[0].filter[1].extension=[ 
    #                         Extension(url="http://cjc_vsmt/auditlog_item",
    #                                     extension = [                   
    #                                         Extension(url="action", valueString = action), 
    #                                         Extension(url="date",   valueString = datestamp ),
    #                                         ]    
    #                                     )
    #                         ]
    # new_filter=ValueSetComposeIncludeFilter(op='=', property='constraint', value=ecl)
    # vs.fhir_valueset.compose.include.append(ValueSetComposeInclude(system='http://snomed.info/sct'))
    # vs.fhir_valueset.compose.include[1].filter=[new_filter]
    # vs.fhir_valueset.compose.include[1].system='http://snomed.info/sct'

    # print("\n".join(fhir_utils.repr_resource(vs.fhir_valueset.compose)))

    # response=requests.put(url=vs.valueset_url, json=json.loads(vs.fhir_valueset.json()))

    # print(response)
