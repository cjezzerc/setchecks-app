#!/usr/bin/env python

import requests

cabbage=requests.get('https://isd.digital.nhs.uk/trud/api/v1/keys/cb210217be013615686ea0ce3de570ae9a789712/items/659/releases')

json_data_as_dict= cabbage.json()

print(json_data_as_dict)

for thing in json_data_as_dict['releases']:
    print(thing['id'], thing['name'])
