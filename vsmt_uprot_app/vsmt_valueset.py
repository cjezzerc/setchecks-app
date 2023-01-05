#!/usr/bin/env python

import sys, json, random, datetime

import requests
import sys

from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeFilter
from fhir.resources.extension import Extension
from fhir.resources.bundle import Bundle

import fhir_utils
import terminology_server_module

class VSMT_ValueSetManager():
    def __init__(self, terminology_server=None):
        self.terminology_server=terminology_server

    def get_vsmt_index_data(self):
        relative_url="ValueSet?_elements=id,title,name,version,url,description,publisher&publisher:contains=VSMT-prototyping"
        stuff=self.terminology_server.do_get(relative_url=relative_url)
        stuff_json_as_dict=stuff.json()
        # print(stuff_json_as_dict)
        print(stuff_json_as_dict['entry'][0]['resource'])
        # valueset_as_fhir=ValueSet.parse_obj(stuff_json_as_dict['entry'][0]['resource'])
        # print(fhir_utils.repr_resource(valueset_as_fhir))

        # bundle_as_fhir=Bundle.parse_obj(stuff_json_as_dict)
        # print(fhir_utils.repr_resource(bundle_as_fhir))
        return None

class VSMT_VersionedValueSet():
    def __init__(self, server_id=None):
        self.valueset_url=('https://r4.ontoserver.csiro.au/fhir/ValueSet/%s' % server_id)
        response=requests.get(url=self.valueset_url)
        valueset_json_as_dict=response.json()
        self.valueset_fhir=ValueSet.parse_obj(valueset_json_as_dict)

    def __repr__(self):
        return "\n".join(fhir_utils.repr_resource(self.valueset_fhir))

if __name__=="__main__":

    terminology_server=terminology_server_module.TerminologyServer(base_url="https://r4.ontoserver.csiro.au/fhir/")
    value_set_manager=VSMT_ValueSetManager(terminology_server=terminology_server)
    d=value_set_manager.get_vsmt_index_data()
    # for k,v in d.items():
    #     print(k,":",v)
    sys.exit()

    server_id="525fd0b7-57d8-48ec-b283-d61a7acd47d4"
    # ecl=sys.argv[1]
    vs=VSMT_VersionedValueSet(server_id=server_id)

    print("\n".join(fhir_utils.repr_resource(vs.valueset_fhir)))


    action = "Added code " + str(random.randint(1000000000000, 3000000000000))
    datestamp=str(datetime.datetime.now())
    vs.valueset_fhir.compose.include[0].filter[1].extension=[ 
                            Extension(url="http://cjc_vsmt/auditlog_item",
                                        extension = [                   
                                            Extension(url="action", valueString = action), 
                                            Extension(url="date",   valueString = datestamp ),
                                            ]    
                                        )
                            ]
    # new_filter=ValueSetComposeIncludeFilter(op='=', property='constraint', value=ecl)
    # vs.valueset_fhir.compose.include.append(ValueSetComposeInclude(system='http://snomed.info/sct'))
    # vs.valueset_fhir.compose.include[1].filter=[new_filter]
    # vs.valueset_fhir.compose.include[1].system='http://snomed.info/sct'

    print("\n".join(fhir_utils.repr_resource(vs.valueset_fhir.compose)))

    response=requests.put(url=vs.valueset_url, json=json.loads(vs.valueset_fhir.json()))

    print(response)
