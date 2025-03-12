#!/usr/bin/python

import sys

from .parse_bundle_message import parse_bundle_message
from .process_report_observations import process_report_observations
from .utils import format_address_item
from .follow_references import follow_references

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
    request_id=[service_request.identifier[0].value] # just take first identifier
    if service_request.requisition is not None:
        requisition_id=service_request.requisition.value
    else:
        requisition_id=None
    requested_tests=[x.display for x in service_request.code.coding]
    requester=service_request.requester.display
    request_date=service_request.authoredOn
    if service_request.note is not None:
        request_note=[x.text for x in service_request.note]
    else:
        request_note=""
    return request_id, requested_tests, requester, request_date, request_note, requisition_id

def process_specimen(specimen=None):
    requester_specimen_id=specimen.identifier[0].value # just take first identifier
    laboratory_accession_id=specimen.accessionIdentifier.value
    specimen_type=specimen.type.coding[0].display # just take first coding
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
    
    resources_by_fullUrl, resources_by_type=parse_bundle_message(
        filename=filename,
        flask_FileStorage=flask_FileStorage,
        )
    
    diagnostic_report, patient, service_requests, specimens, primary_observations=follow_references(
        resources_by_fullUrl=resources_by_fullUrl, 
        resources_by_type=resources_by_type,
        )

    text_report_strings=[]

    text_report_strings.append(f"dr: {diagnostic_report.id}")
    text_report_strings.append(f"p: {patient.id}")
    text_report_strings.append(f"sr: {[x.id for x in service_requests]}")
    text_report_strings.append(f"sp: {[x.id for x in specimens]}")
    text_report_strings.append(f"po: {[x.id for x in primary_observations]}")
    
    nhs_number, name, address, dob, gender=process_patient(patient_resource=patient)
    
    text_report_strings.append("")
    text_report_strings.append(f'NHS Number: {nhs_number}')
    text_report_strings.append(f'Name:       {name}')
    text_report_strings.append(f'Address:    {address}')
    text_report_strings.append(f'DOB:        {dob}')
    text_report_strings.append(f'Gender:     {gender}')

    for service_request in service_requests:
        request_id, requested_tests, requester, request_date, request_note, requisition_id=process_service_request(
            service_request=service_request,
            )
        text_report_strings.append("")
        text_report_strings.append(f'Request Id:        {request_id}')
        text_report_strings.append(f'Requisition Id:    {requisition_id}')
        text_report_strings.append(f'Requested test(s): {requested_tests}')
        text_report_strings.append(f'Requester:         {requester}')
        text_report_strings.append(f'Request date:      {request_date}')
        text_report_strings.append(f'Comments:          {request_note}')

    for specimen in specimens: 
        requester_specimen_id, laboratory_accession_id, specimen_type, collected_date, received_date=process_specimen(
            specimen=specimen,
            )
        text_report_strings.append("")
        text_report_strings.append(f'Requester Specimen Id:   {requester_specimen_id}')
        text_report_strings.append(f'Laboratory Accession Id: {laboratory_accession_id}')
        text_report_strings.append(f'Specimen Type:           {specimen_type}')
        text_report_strings.append(f'Collected Date:          {collected_date}')
        text_report_strings.append(f'Received Date:           {received_date}')
        text_report_strings.append("")

    output_strings=process_report_observations(
        primary_observations=primary_observations,
        resources_by_fullUrl=resources_by_fullUrl,
        )
    
    for output_string in output_strings:
        text_report_strings.append(output_string)

    comments=diagnostic_report.conclusion
    text_report_strings.append("")
    text_report_strings.append(f"Comments: {comments}" )

    return text_report_strings

if __name__=="__main__":
    report_fhir_bundle_filename=sys.argv[1]
    text_report_strings=process_fhir_bundle_report_to_text(
        filename=report_fhir_bundle_filename)
    print("\n".join(text_report_strings))
    
