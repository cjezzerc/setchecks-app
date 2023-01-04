#################################################
# "parse" FHIR Parameters object to             #
# represent a SNOMED concept more appropriately #
#################################################

def parse_parameters_resource_from_snomed_concept_lookup(parameters=None):
    concept_attributes={}
    concept_attributes['designation']=[] 
    for parameter in parameters.parameter:
        name=parameter.name
        non_name_keys=list(parameter.__fields_set__)
        non_name_keys.remove('name')
        non_name_key=non_name_keys[0]
        value=getattr(parameter, non_name_key)
        if name not in ['property', 'designation']: 
            assert name not in concept_attributes
            concept_attributes[name]=value
            # print("%3s : %15s : %s" % (i_entry, name, value))
        elif name =='property':
            k,v = get_property_name_and_value(parameter.part)
            if k in ['child','parent','609096000','123005000']: # last two are role-group and part-of
                if k not in concept_attributes:
                    concept_attributes[k]=[] # as do not know a priori how many entries may be seen for a particular 'property'
                                            # then initialise all as lists
                concept_attributes[k].append(v)
            else:
                assert k not in concept_attributes # these keys should only occur once
                concept_attributes[k]=v
        else:  # i.e. name == designation
            concept_attributes['designation'].append(get_designation_language_use_value(parameter.part))
        # print("--------------------------------------------------")
    return concept_attributes

###########################################
# helper functions for parsing parameters #
# as a SNOMED concept                     #
###########################################

def get_property_name_and_value(part):
    name=None
    value=None
    for d in part:
        if d.name=='code':
            name=d.valueCode
        if d.name=='value':
            if d.valueCode is not None:
                value=d.valueCode
            elif d.valueString is not None:
                value=d.valueString
            elif d.valueBoolean is not None:
                value=d.valueBoolean
            else:
                print("No suitable value found in ", d)
                sys.exit()
        if d.name=='subproperty':
            if value is None:
                value=[]
            value.append(get_property_name_and_value(d.part)) # recursive call, but only expect it to go one deep
    return [name, value]

def get_designation_language_use_value(part):
    designation_dict={'language':None, 'use': None, 'value': None}
    for d in part:
        if d.name=='language':
            designation_dict['language']=d.valueCode
        if d.name=='use':
            designation_dict['use']=d.valueCoding.display
        if d.name=='value':
            designation_dict['value']=d.valueString
    return designation_dict