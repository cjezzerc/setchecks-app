#!/usr/bin/env python

import sys, json, random, datetime

import requests
import sys

from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeFilter
from fhir.resources.extension import Extension
from fhir.resources.bundle import Bundle
from fhir.resources.identifier import Identifier

import fhir_utils
import terminology_server_module

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
            k=index_item.vsmt_identifier+":"+index_item.vsmt_version
            if k in vsmt_index:
                print("FATAL ERROR: The key %s has already been seen in the index" % k)
                sys.exit()
            else:
                vsmt_index[k]=index_item
        return vsmt_index

class VSMT_IndexItem():

    def __init__(self, vsmt_version=None, vsmt_identifier=None, vsmt_human_name=None, server_id=None, server_vsn=None):
        self.vsmt_version=vsmt_version
        self.vsmt_identifier=vsmt_identifier
        self.vsmt_human_name=vsmt_human_name
        self.server_id=server_id
        self.server_vsn=server_vsn

    def __repr__(self):
        return "VSMT_identifier: %5s | vsn: %3s | server_id: %32s | server_vsn: %3s | name: %s" % (self.vsmt_identifier, 
                                                                                            self.vsmt_version,
                                                                                            self.server_id,
                                                                                            self.server_vsn, 
                                                                                            self.vsmt_human_name,)

########################
# VSMT_VersionValueSet #
########################

class VSMT_VersionedValueSet():
    def __init__(self, terminology_server=None, server_id=None, title=None):
        if (server_id and title) or (not (server_id or title)): # must specify ONLY ONE of server_id or title
                                                                # if title specified then will create new value set on server??
            self=None

        if server_id:
            self.terminology_server=terminology_server
            # self.valueset_url=(terminology_server.base_url + '/ValueSet/%s' % server_id)
            # response=requests.get(url=self.valueset_url)
            relative_url='/ValueSet/%s' % server_id
            response=terminology_server.do_get(relative_url=relative_url)
            valueset_json_as_dict=response.json()
            self.fhir_valueset=ValueSet.parse_obj(valueset_json_as_dict)

        if title:
            # self.valueset_url=None  # at first creation not stored to server immediately
            #                         # first store will require specification of terminology server or will fail
            self.fhir_valueset=ValueSet(title=title, publisher='VSMT-prototyping', status='draft', url='http:vsmt-prototyping', identifier=[Identifier(value="VSMT_????")], version="??")
            self.terminology_server=terminology_server

    def get_vsmt_identifier(self):
        try:
            return self.fhir_valueset.identifier[0].value
        except:
            return None

    def store_to_server(self, verbose=False):
        if self.fhir_valueset.id==None:  
            relative_url="/ValueSet" 
            response=self.terminology_server.do_post(relative_url, json=json.loads(self.fhir_valueset.json()), verbose=verbose)
        else:
            relative_url="/ValueSet/%s" % self.fhir_valueset.id
            response=self.terminology_server.do_put(relative_url, json=json.loads(self.fhir_valueset.json()), verbose=verbose)
        return(response)
        
        
    def __str__(self):
        return "\n".join(fhir_utils.repr_resource(self.fhir_valueset))

####################################
# code checking during deveeloment #
####################################

if __name__=="__main__":

    terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    value_set_manager=VSMT_ValueSetManager(terminology_server=terminology_server)
    vsmt_index=value_set_manager.get_vsmt_index_data()
    
    for k, v in vsmt_index.items():
        print("%15s - %s" % (k,v))

    # server_id=vsmt_index['VSMT_1645:3'].server_id
    # vs=VSMT_VersionedValueSet(terminology_server=terminology_server, server_id=server_id)
    # # print(vs)
    # print("VSMT_identifier:",vs.get_vsmt_identifier())

    # vs=VSMT_VersionedValueSet(title='cjc My first value set', terminology_server=terminology_server)
    # print(vs)
    # r=vs.store_to_server(verbose=True)
    # print(r.json())
    # print("VSMT_identifier:",vs.get_vsmt_identifier())

   

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
