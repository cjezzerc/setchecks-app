
# from process_path_lab_test_report.process_observation import process_observation
# from process_path_lab_test_report.utils import trim_id
from .process_observation import process_observation
from .utils import trim_id


def process_report_observations(
    resources_by_id=None,
    resources_by_type=None,
    ):
 
    message_header=resources_by_type["MessageHeader"][0]
    message_header_focus_id=trim_id(message_header.focus[0].reference.strip())
    message_header_focus_r=resources_by_id[message_header_focus_id]
    diagnostic_report=message_header_focus_r

    output_strings=[]

    for i_result, result in enumerate(diagnostic_report.result):
        observation=resources_by_id[trim_id(result.reference)]
        output_strings=process_observation(
            observation=observation, 
            output_strings=output_strings, 
            resources_by_id=resources_by_id,
            )

    return output_strings