import requests
import os

from fhir.resources.valueset import ValueSet

class TerminologyServer():
    def __init__(self, base_url=None, auth_url=None):
        self.base_url=base_url
        self.auth_url=auth_url
        self.get_jwt_token()

    def get_jwt_token(self):
        openid_data={}
        openid_data['client_id']=os.environ['ONTOSERVER_USERNAME']
        openid_data['client_secret']=os.environ['ONTOSERVER_SECRET']
        openid_data['grant_type']='client_credentials'
        r=requests.post(url=self.auth_url, data=openid_data)
        # print(r.json())
        access_token=r.json()['access_token']
        self.headers={}
        self.headers['Authorization'] = 'Bearer %s' % access_token

    def do_get(self, relative_url=None, verbose=False, timing=False):
        # print(self.base_url)
        # print(relative_url)
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("GET: %s" % url)
        r=requests.get(url=url, headers=self.headers)
        # print(r)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r

    def do_put(self, relative_url=None, json=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("PUT: %s" % url)
        r=requests.put(url, json=json, headers=self.headers)
        # print(r)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r    
    
    def do_post(self, relative_url=None, json=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("POST: %s" % url)
        r=requests.post(url, json=json, headers=self.headers)
        # print("POST RESPONSE:::::::::", r.text)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r    
    

    def do_delete(self, relative_url=None, verbose=False, timing=False):
        url=self.base_url + "/" + relative_url
        if timing:
            start_time=time.time()
        if verbose:
            print("DELETE: %s" % url)
        r=requests.delete(url, headers=self.headers)
        if timing:
            print("That took (in seconds)", time.time()-start_time)
        return r  
    
    def do_expand(self, ecl=None, refset_id=None, value_set_server_id=None, sct_version=None, add_display_names=False):
        
        one_and_only_one_defined=sum([int(bool(x not in ["", None])) for x in [ecl, refset_id, value_set_server_id]])==1
        if not one_and_only_one_defined:
            print("Require one and only one of ecl and value_set_server_id to be defined in expand_ecl")
            print("ecl", ecl)
            print("value_set_server_id", value_set_server_id)
            sys.exit()

        
        if ecl: # expand a piece of ecl as implicit ValueSet
            # print("=> ECL", ecl)
            # relative_url= "ValueSet/$expand?url=%s?fhir_vs=ecl/(%s)" % (sct_version, ecl)
            if sct_version:
                relative_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)" % (sct_version, ecl)
            else:
                relative_url= "ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=ecl/(%s)" % (ecl)
        elif refset_id: # expand a SNOMED refset as implicit ValueSet
            if sct_version:
                relative_url= "ValueSet/$expand?url=%s?fhir_vs=refset/%s" % (sct_version, refset_id)
            else:
                relative_url= "ValueSet/$expand?url=http://snomed.info/sct?fhir_vs=refset/%s" % (refset_id)
        else: # expand an implicit ValueSet
            if sct_version:
                relative_url= "ValueSet/%s/$expand?system-version=http://snomed.info/sct%%7C%s" % (value_set_server_id, sct_version)
            else:
                relative_url= "ValueSet/%s/$expand" % (value_set_server_id)
        # print(relative_url)
        response=self.do_get(relative_url=relative_url, verbose=False) 
        print(response)
        # print(response.json())
        if response.json()["resourceType"]=="ValueSet": 
            ecl_response=[]
            extensional_valueset=ValueSet.parse_obj(response.json())
            if extensional_valueset.expansion.contains:
                for contained_item in extensional_valueset.expansion.contains:
                    if add_display_names:
                        ecl_response.append("%20s | %s | (inactive=%s)" % (contained_item.code, contained_item.display, contained_item.inactive))
                    else:
                        ecl_response.append(int(contained_item.code)) # trial addition12 jan22 
            return ecl_response
        else:
            return None # Need to decide way to send back more diagnostic output

    

    # def expand_value_set(self, *, value_set_server_id):
    #     relative_url= "ValueSet/%s/$expand" % (value_set_server_id)
    #     print(relative_url)
    #     response=self.do_get(relative_url=relative_url) 
    #     return response.json()
    #     # expanded_value_set=ValueSet.parse_obj(response.json())
    #     # return expanded_value_set

