""" function to pull version list from terminology server and convert to date sorted list of SCT objects"""

import os
from flask import current_app
from . import sct_version
from fhir.resources.bundle import Bundle
import setchks_app.terminology_server_module
from setchks_app.fhir_utils.fhir_utils import repr_resource

def get_sct_versions():

        terminology_server=setchks_app.terminology_server_module.TerminologyServer()
        relative_url= "CodeSystem?url=http://snomed.info/sct"
        response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
        bundle=Bundle.parse_obj(response.json())

        for be in bundle.entry:
            print("\n".join(repr_resource(resource=be.resource)))

        available_sct_versions=[be.resource.dict()["version"] for be in bundle.entry]
        available_sct_versions=[sct_version.SctVersion(formal_version_string=x) for x in available_sct_versions]
        available_sct_versions.sort(key=get_sortable_date_part, reverse=True) # mild overkill since as it stands sorting on 
                                                                                # whole formal_version_string would work
        return available_sct_versions


def get_sortable_date_part(sct_version):
    return sct_version.date_string
