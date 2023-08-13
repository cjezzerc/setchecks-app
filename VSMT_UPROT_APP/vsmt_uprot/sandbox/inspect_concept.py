#!/usr/bin/env python

import os, sys, pprint, json



# import VSMT prototyping modules
sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP/')
from vsmt_uprot.terminology_server_module import TerminologyServer

import vsmt_uprot.fhir_utils
from vsmt_uprot.fhir_snomed_utils import parse_parameters_resource_from_snomed_concept_lookup
from fhir.resources.parameters import Parameters

terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])

releases=["20230412","20230315","20230215","20230118","20221221","20221123","20221026","20220928","20220831","20220803","20220706","20220608","20220511"]
release=releases[-1]

sct_version="http://snomed.info/sct/83821000000107/version/" + release
sct_id=91487003

sub_url="CodeSystem/$lookup?code=%s&system=http://snomed.info/sct&version=%s&property=%s" % (sct_id, sct_version,"*")
concept_parameters=terminology_server.do_get(relative_url=sub_url).json()
fhir_concept_resource=Parameters.parse_obj(concept_parameters)
stuff=parse_parameters_resource_from_snomed_concept_lookup(parameters=fhir_concept_resource)
for k,v in stuff.items():
    print(k,v)