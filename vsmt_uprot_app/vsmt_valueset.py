#!/usr/bin/env python

import sys, json, random, datetime

import requests
import sys

from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeFilter
from fhir.resources.extension import Extension
from fhir.resources.bundle import Bundle

import fhir_utils
import terminology_server_module

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

class VSMT_VersionedValueSet():
    def __init__(self, server_id=None):
        self.valueset_url=('https://r4.ontoserver.csiro.au/fhir/ValueSet/%s' % server_id)
        response=requests.get(url=self.valueset_url)
        valueset_json_as_dict=response.json()
        self.valueset_fhir=ValueSet.parse_obj(valueset_json_as_dict)

    def __str__(self):
        return "\n".join(fhir_utils.repr_resource(self.valueset_fhir))

if __name__=="__main__":

    terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    value_set_manager=VSMT_ValueSetManager(terminology_server=terminology_server)
    vsmt_index=value_set_manager.get_vsmt_index_data()
    
    for k, v in vsmt_index.items():
        print("%15s - %s" % (k,v))

    server_id=vsmt_index['VSMT_1645:3'].server_id
    vs=VSMT_VersionedValueSet(server_id=server_id)

    print(vs)

    # action = "Added code " + str(random.randint(1000000000000, 3000000000000))
    # datestamp=str(datetime.datetime.now())
    # vs.valueset_fhir.compose.include[0].filter[1].extension=[ 
    #                         Extension(url="http://cjc_vsmt/auditlog_item",
    #                                     extension = [                   
    #                                         Extension(url="action", valueString = action), 
    #                                         Extension(url="date",   valueString = datestamp ),
    #                                         ]    
    #                                     )
    #                         ]
    # new_filter=ValueSetComposeIncludeFilter(op='=', property='constraint', value=ecl)
    # vs.valueset_fhir.compose.include.append(ValueSetComposeInclude(system='http://snomed.info/sct'))
    # vs.valueset_fhir.compose.include[1].filter=[new_filter]
    # vs.valueset_fhir.compose.include[1].system='http://snomed.info/sct'

    # print("\n".join(fhir_utils.repr_resource(vs.valueset_fhir.compose)))

    # response=requests.put(url=vs.valueset_url, json=json.loads(vs.valueset_fhir.json()))

    # print(response)
