def process_service_request(service_request=None):
    request_id=service_request.identifier[0].value # just take first identifier
    if service_request.requisition is not None:
        requisition_id=service_request.requisition.value
    else:
        requisition_id=""
    requested_coding=service_request.code.coding[0] # just take first coding
    requested_test=f"{requested_coding.code}:{requested_coding.display}" 
    requester=service_request.requester.display
    request_date=service_request.authoredOn
    
    if service_request.reasonCode is not None:
        clinical_details=service_request.reasonCode[0].text # just take first reasonCode 
    else:
        clinical_details=""
    
    if service_request.note is not None:
        request_note=[x.text for x in service_request.note]
    else:
        request_note=""
    return request_id, requested_test, requester, request_date, clinical_details, request_note, requisition_id