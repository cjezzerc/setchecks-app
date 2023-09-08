""" function to pull version list from terminology server and convert to date sorted list of SCT objects"""

import os
from . import sct_version
import vsmt_uprot.terminology_server_module
from fhir.resources.bundle import Bundle

def get_sct_versions():

        terminology_server=vsmt_uprot.terminology_server_module.TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                            auth_url=os.environ["ONTOAUTH_INSTANCE"])
        relative_url= "CodeSystem?url=http://snomed.info/sct"
        response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
        bundle=Bundle.parse_obj(response.json())

        available_sct_versions=[be.resource.dict()["version"] for be in bundle.entry]
        available_sct_versions=[sct_version.SctVersion(formal_version_string=x) for x in available_sct_versions]
        available_sct_versions.sort(key=get_sortable_date_part, reverse=True) # mild overkill since as it stands sorting on 
                                                                                # whole formal_version_string would work
        return available_sct_versions


def get_sortable_date_part(sct_version):
    return sct_version.date_string
