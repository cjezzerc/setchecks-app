import requests

from fhir.resources.valueset import ValueSet

def do_get(url=None, verbose=False, timing=False):
    if timing:
        start_time=time.time()
    if verbose:
        print("GET: %s" % url)
    r=requests.get(url)
    if timing:
        print("That took (in seconds)", time.time()-start_time)
    return r
    
def expand_ecl(ecl=None, version=None):
        # url='https://r4.ontoserver.csiro.au/fhir/ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=ecl/(%s)' % ecl
        url='https://r4.ontoserver.csiro.au/fhir/ValueSet/$expand?url=%s?fhir_vs=ecl/(%s)' % (version, ecl)
        # print("===>>>>", url)
    
        response=do_get(url) # requests.get(url=url)
        ecl_response=[]
        if response.json()["resourceType"]=="ValueSet": 
            extensional_valueset=ValueSet.parse_obj(response.json())
            if extensional_valueset.expansion.contains:
                for contained_item in extensional_valueset.expansion.contains:
                    ecl_response.append(contained_item.code) #, contained_item.display
        return ecl_response