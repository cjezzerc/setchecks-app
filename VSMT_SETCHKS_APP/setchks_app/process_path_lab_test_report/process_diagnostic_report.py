from .utils import format_address_item

def process_diagnostic_report(diagnostic_report=None, resources_by_fullUrl=None):
    report_id=diagnostic_report.identifier[0].value # just take first identifier
    issued_date=diagnostic_report.issued
    provider_name=resources_by_fullUrl[diagnostic_report.performer[0].reference].name       # assumes only one performer, that reference exists,
    provider_address=format_address_item(resources_by_fullUrl[diagnostic_report.performer[0].reference].address[0]) # and that it is an Organization with one address
    return report_id, issued_date, provider_name, provider_address