#!/usr/bin/python

import sys

from .parse_bundle_message import parse_bundle_message
from .process_report_observations import process_report_observations
from .utils import format_address_item

def process_patient(patient_resource=None):
    nhs_number=patient_resource.identifier[0].value # assumes NHS number is first identifier
    
    name_item=patient_resource.name[0] # just taking the first of available full names
    name=name_item.family            
    for given in name_item.given:
        name+=", "+given

    address=format_address_item(address_item=patient_resource.address[0]) # just taking first of avaialble addresses  
    dob=patient_resource.birthDate
    gender=patient_resource.gender
    return nhs_number, name, address, dob, gender

def process_service_request(service_request=None):
    request_id=[service_request.identifier[0].value]
    requested_tests=[x.display for x in service_request.code.coding]
    requester=service_request.requester.display
    request_date=service_request.authoredOn
    if service_request.note is not None:
        request_note=[x.text for x in service_request.note]
    else:
        request_note=""
    return request_id, requested_tests, requester, request_date, request_note

def process_specimen(specimen=None):
    requester_specimen_id=specimen.identifier[0].value
    laboratory_accession_id=specimen.accessionIdentifier.value
    specimen_type=specimen.type.coding[0].display
    collected_date=specimen.collection.collectedDateTime
    received_date=specimen.receivedTime
    return requester_specimen_id, laboratory_accession_id, specimen_type, collected_date, received_date

def process_fhir_bundle_report_to_text(
    filename=None, 
    flask_FileStorage=None
    ):
    
    # This routine can be called from a Flask app or a plain script
    # It accepts either 
    #     a filename 
    #     a flask FileStorage object 
    # These are passed on to parse_bundle_message which handle the distinction
    # (depending on which one is not None)
    
    resources_by_id, resources_by_type=parse_bundle_message(
        filename=filename,
        flask_FileStorage=flask_FileStorage,
        )
    
    text_report_strings=[]
    
    nhs_number, name, address, dob, gender=process_patient(
        patient_resource=resources_by_type["Patient"][0],
        )
    text_report_strings.append("")
    text_report_strings.append(f'NHS Number: {nhs_number}')
    text_report_strings.append(f'Name:       {name}')
    text_report_strings.append(f'Address:    {address}')
    text_report_strings.append(f'DOB:        {dob}')
    text_report_strings.append(f'Gender:     {gender}')

    request_id, requested_tests, requester, request_date, request_note=process_service_request(
        service_request=resources_by_type["ServiceRequest"][0],
        )
    text_report_strings.append("")
    text_report_strings.append(f'Request Id:        {request_id}')
    text_report_strings.append(f'Requested test(s): {requested_tests}')
    text_report_strings.append(f'Requester:         {requester}')
    text_report_strings.append(f'Request date:      {request_date}')
    text_report_strings.append(f'Note(s):           {request_note}')

    for specimen in resources_by_type["Specimen"]:
        requester_specimen_id, laboratory_accession_id, specimen_type, collected_date, received_date=process_specimen(
            specimen=specimen,
            )
        text_report_strings.append("")
        text_report_strings.append(f'Requester Specimen Id:  {requester_specimen_id}')
        text_report_strings.append(f'Laboratory Accession Id: {laboratory_accession_id}')
        text_report_strings.append(f'Specimen Type:         {specimen_type}')
        text_report_strings.append(f'Collected Date:         {collected_date}')
        text_report_strings.append(f'Received Date:          {received_date}')

    output_strings=process_report_observations(
        resources_by_id=resources_by_id,
        resources_by_type=resources_by_type,
        )
    for output_string in output_strings:
        text_report_strings.append(output_string)

    comments=resources_by_type["DiagnosticReport"][0].conclusion
    text_report_strings.append("")
    text_report_strings.append(f"Comments: {comments}" )

    return text_report_strings

if __name__=="__main__":
    report_fhir_bundle_filename=sys.argv[1]
    text_report_strings=process_fhir_bundle_report_to_text(
        filename=report_fhir_bundle_filename)
    print("\n".join(text_report_strings))
    
