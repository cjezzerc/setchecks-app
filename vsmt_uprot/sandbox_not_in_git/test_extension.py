#!/usr/bin/env python

import requests
import json
import pprint
import time
import sys
from fhir.resources.valueset import ValueSet
from fhir.resources.identifier import Identifier
from fhir.resources.extension import Extension
sys.path.append("../")
import repr_fhir_resource
import datetime
import random

# c789d76c-4b7e-4469-9921-cafe69083736
id="525fd0b7-57d8-48ec-b283-d61a7acd47d4"

valueset_url='https://r4.ontoserver.csiro.au/fhir/ValueSet/'+id
response=requests.get(url=valueset_url)
valueset_json_as_dict=response.json()
valueset_fhir=ValueSet.parse_obj(valueset_json_as_dict)

print("===== As received from ontoserver ======")
print("\n".join(repr_fhir_resource.repr_resource(valueset_fhir)))
print("===========")

valueset_fhir.identifier=[Identifier(value="cjc_woz_on_FHIR_ere")]

# valueset_fhir.extension=None
if not valueset_fhir.extension:
    valueset_fhir.extension=[]

action = "Added code " + str(random.randint(1000000000000, 3000000000000))
datestamp=str(datetime.datetime.now())
valueset_fhir.extension+=[ 
                          Extension(url="http://cjc_vsmt/auditlog_item",
                                    extension = [                   
                                        Extension(url="action", valueString = action), 
                                        Extension(url="date",   valueString = datestamp ),
                                        ]    
                                    )
                        ]

print(valueset_fhir.json())
print(type(valueset_fhir.json()))

values_set_fhir_dict=json.loads(valueset_fhir.json())

response=requests.put(url=valueset_url, json=values_set_fhir_dict)

print("===== After amend ======")
print("\n".join(repr_fhir_resource.repr_resource(valueset_fhir)))
print("========================")

print(response)
# print(response.text)
# print(response.json())
