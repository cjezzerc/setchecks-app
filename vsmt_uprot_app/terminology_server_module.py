import requests

from fhir.resources.valueset import ValueSet

class TerminologyServer():
    def __init__(self, base_url=None):
        self.base_url=base_url

    def do_get(self, relative_url=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("GET: %s" % url)
        r=requests.get(url)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r
    
    def expand_ecl(self, ecl=None, sct_version=None, add_display_names=False):
        relative_url= "ValueSet/$expand?url=%s?fhir_vs=ecl/(%s)" % (sct_version, ecl)
        print(relative_url)
        response=self.do_get(relative_url=relative_url) 
        print(response)
        if response.json()["resourceType"]=="ValueSet": 
            ecl_response=[]
            extensional_valueset=ValueSet.parse_obj(response.json())
            if extensional_valueset.expansion.contains:
                for contained_item in extensional_valueset.expansion.contains:
                    if add_display_names:
                        ecl_response.append("%20s | %s |" % (contained_item.code, contained_item.display))
                    else:
                        ecl_response.append(contained_item.code) 
            return ecl_response
        else:
            return None