""" function to pull version list from terminology server and convert to date sorted list of SCT objects"""

import os

from flask import current_app
from fhir.resources.bundle import Bundle

from . import sct_version
import setchks_app.terminology_server_module
from setchks_app.descriptions_service.descriptions_service import DescriptionsService


def get_sct_versions_on_ontoserver():

    terminology_server=setchks_app.terminology_server_module.TerminologyServer()
    relative_url= "CodeSystem?url=http://snomed.info/sct"
    response=terminology_server.do_get(relative_url=relative_url, verbose=True) 
    bundle=Bundle.parse_obj(response.json())

    # for be in bundle.entry:
    #     print("\n".join(repr_resource(resource=be.resource)))

    available_sct_versions_on_ontoserver=[be.resource.dict()["version"] for be in bundle.entry]
    available_sct_versions_on_ontoserver=[sct_version.SctVersion(formal_version_string=x) for x in available_sct_versions_on_ontoserver]
    available_sct_versions_on_ontoserver.sort(key=get_sortable_date_part, reverse=True) # mild overkill since as it stands sorting on 
                                                                            # whole formal_version_string would work
    return available_sct_versions_on_ontoserver


def get_sortable_date_part(sct_version):
    return sct_version.date_string

def get_sct_versions_available_in_app():
    all_available_sct_versions={x.date_string: x for x in get_sct_versions_on_ontoserver()}
    available_sct_versions_in_app=[]
    ds=DescriptionsService(data_type="hst")
    hst_dict=ds.check_whether_releases_on_ontoserver_have_collections()
    for sct_version, hst_exists in hst_dict.items():
        if hst_exists: # only make sct_version available if has an HST 
            available_sct_versions_in_app.append(all_available_sct_versions[sct_version])
    return available_sct_versions_in_app


                
