from .utils import format_address_item, format_none_to_null_string

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