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

    def do_put(self, relative_url=None, json=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("PUT: %s" % url)
        r=requests.put(url, json=json)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r    
    
    def do_post(self, relative_url=None, json=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("POST: %s" % url)
        r=requests.post(url, json=json)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r    
    
    def do_expand(self, ecl=None, value_set_server_id=None, sct_version=None, add_display_names=False):
        
        one_and_only_one_defined=sum([int(bool(x not in ["", None])) for x in [ecl, value_set_server_id]])==1
        if not one_and_only_one_defined:
            print("Require one and only one of ecl and value_set_server_id to be defined in expand_ecl")
            print("ecl", ecl)
            print("value_set_server_id", value_set_server_id)
            sys.exit()

        if ecl:
            relative_url= "ValueSet/$expand?url=%s?fhir_vs=ecl/(%s)" % (sct_version, ecl)
        else:
            if sct_version:
                relative_url= "ValueSet/%s/$expand?system-version=%s" % (value_set_server_id, sct_version)
            else:
                relative_url= "ValueSet/%s/$expand" % (value_set_server_id)
        print(relative_url)
        response=self.do_get(relative_url=relative_url, verbose=True) 
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

    # def expand_value_set(self, *, value_set_server_id):
    #     relative_url= "ValueSet/%s/$expand" % (value_set_server_id)
    #     print(relative_url)
    #     response=self.do_get(relative_url=relative_url) 
    #     return response.json()
    #     # expanded_value_set=ValueSet.parse_obj(response.json())
    #     # return expanded_value_set

