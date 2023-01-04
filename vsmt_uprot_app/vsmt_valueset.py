#!/usr/bin/env python

import sys, json, random, datetime

import requests

from fhir.resources.valueset import ValueSet, ValueSetCompose, ValueSetComposeInclude, ValueSetComposeIncludeFilter
from fhir.resources.extension import Extension

import fhir_utils

class VsmtValueSet():
    def __init__(self, server_id=None):
        self.valueset_url=('https://r4.ontoserver.csiro.au/fhir/ValueSet/%s' % server_id)
        response=requests.get(url=self.valueset_url)
        valueset_json_as_dict=response.json()
        self.valueset_fhir=ValueSet.parse_obj(valueset_json_as_dict)

    def __repr__(self):
        return "\n".join(fhir_utils.repr_resource(self.valueset_fhir))

if __name__=="__main__":
    server_id="525fd0b7-57d8-48ec-b283-d61a7acd47d4"
    # ecl=sys.argv[1]
    vs=VsmtValueSet(server_id=server_id)

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
