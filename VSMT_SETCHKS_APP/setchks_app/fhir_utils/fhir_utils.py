import sys
import pprint

def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

###########################################
# format resource to show "dot" notation  #
# of object hierarchy and values          #
###########################################

def repr_resource(resource=None, repr_strings=None, indent=0, object_representation="resource"):
    # print(resource)
    # Logic of this is fairly tricky.
    # Also, feel should be neater way to code this so that in recursive calls do not both update repr_string in place AND return it
    # (see comment at end)
    # but could not get neater version to work so kept it like this
    if repr_strings==None:
        repr_strings=[]
    indent_string=" "*indent
    # padding_string=" "*(20)
    padding_string=" "*(20-indent)   # this form keeps colons aligned - not sure which prefer
    if type(resource)==list:
        for i_thing, thing in enumerate(resource):
            repr_resource(thing, repr_strings=repr_strings, indent=indent+3, object_representation=object_representation+"["+str(i_thing)+"]")
            if i_thing!=len(resource)-1:
                repr_strings.append('    %s---' % (indent_string))
            else:
                pass
                # repr_strings.append('\n\n')

    else:
        # import pdb; pdb.set_trace()
        # for thing_name, thing_value in resource:
        for putative_tuple in resource:
            # print (putative_tuple) # uncomment for debugging contents of putative_tuple
            thing_name, thing_value = putative_tuple
            if (thing_value is not None): 
                t=type(thing_value)
                if (t is not str) and iterable(thing_value) and (not (type(thing_value)==list and type(thing_value[0])==str)):
                    if type(thing_value)==list:
                        decorator="[0..%s]" % len(thing_value)
                    else:
                        decorator="..."
                    repr_strings.append("%s %-50s %s:" % (indent_string, object_representation+"."+thing_name+decorator, padding_string))
                    
                    repr_resource(thing_value, repr_strings=repr_strings, indent=indent+3, object_representation=object_representation+"."+thing_name)
                else:
                    repr_strings.append("%s %-50s %s: %s" % (indent_string, object_representation+"."+thing_name, padding_string, thing_value))
    return repr_strings # this is only relevant when finally exit at very end after all recursion done
                        # see comment at top



