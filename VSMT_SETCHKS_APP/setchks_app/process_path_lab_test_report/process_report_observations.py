
from .process_observation import process_observation


def process_report_observations(
    resources_by_fullUrl=None,
    resources_by_type=None,
    ):
 
    message_header=resources_by_type["MessageHeader"][0]
    message_header_focus_fullUrl=message_header.focus[0].reference.strip()
    message_header_focus_r=resources_by_fullUrl[message_header_focus_fullUrl]
    diagnostic_report=message_header_focus_r

    output_strings=[]

    for i_result, result in enumerate(diagnostic_report.result):
        observation=resources_by_fullUrl[result.reference]
        output_strings=process_observation(
            observation=observation, 
            output_strings=output_strings, 
            resources_by_fullUrl=resources_by_fullUrl,
            )

    return output_strings