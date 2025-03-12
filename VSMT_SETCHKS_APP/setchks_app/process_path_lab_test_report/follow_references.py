from .parse_value import parse_value_entity

def follow_references(
    resources_by_fullUrl=None, 
    resources_by_type=None
    ):
    """ 
    start from MessageHeader and follow references through DiagnosticReport
    to Patient, ServiceRequests, Specimens, and Observations (only those directly referenced in DiagnosticReport)
    """
    message_header=resources_by_type["MessageHeader"][0] # assume there is one and only one
    diagnostic_report=resources_by_fullUrl[message_header.focus[0].reference.strip()] # assume this reference exists
    patient=resources_by_fullUrl[diagnostic_report.subject.reference] # assume this reference exists

    service_requests=       [resources_by_fullUrl[x.reference] for x in diagnostic_report.basedOn]
    specimens=              [resources_by_fullUrl[x.reference] for x in diagnostic_report.specimen]
    primary_observations=   [resources_by_fullUrl[x.reference] for x in diagnostic_report.result]

    return diagnostic_report, patient, service_requests, specimens, primary_observations