###########
# trim_id #
###########

def trim_id(id_string):
    if id_string[:9]=="urn:uuid:":
        id_string=id_string[9:]
    return id_string

#######################
# format_address_item #
#######################

def format_address_item(address_item=None):
    address=""
    for line in address_item.line:
        address+=line + ", "
    for address_part in (address_item.city, address_item.district, address_item.postalCode):
        if address_part is not None:
            address+=address_part+", "
    address=address.strip()
    return address