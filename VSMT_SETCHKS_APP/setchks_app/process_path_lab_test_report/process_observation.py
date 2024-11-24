# from process_path_lab_test_report.parse_value import parse_value_entity
# from process_path_lab_test_report.utils import trim_id
from .parse_value import parse_value_entity
from .utils import trim_id

def process_observation(observation=None, output_strings=None, resources_by_id=None):
    if observation.meta.profile[0]=="https://fhir.hl7.org.uk/StructureDefinition/UKCore-Observation-LabGroup":
        output_strings.append("\n"+observation.code.coding[0].display)
        for member_id in observation.hasMember:
            member_observation=resources_by_id[trim_id(member_id.reference)]
            process_observation(
                 observation=member_observation, 
                 output_strings=output_strings, 
                 resources_by_id=resources_by_id
                 )
    else:
        parsed_value, reference_low, reference_high, reference_text=parse_value_entity(observation)
        display=observation.code.coding[0].display
        code=observation.code.coding[0].code
        if reference_text=="No reference range information":
            formatted_output=(f"{code:18} | {display:55} | {str(parsed_value):16}")
        else:
            formatted_output=(
                f"{code:18} | {display:55} | {str(parsed_value):16} (reference: {str(reference_low):16} - {str(reference_high):16}) ({reference_text})" 
                )
        output_strings.append(formatted_output)
    return output_strings

