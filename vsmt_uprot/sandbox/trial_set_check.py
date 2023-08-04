#!/usr/bin/env python
import sys

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/')

import vsmt_uprot.setchks.setchk_definitions 
from vsmt_uprot.setchks.setchks_session import SetchksSession

setchk=vsmt_uprot.setchks.setchk_definitions.setchks['a_test_check']
setchks_session=SetchksSession()

fh=open('trial1.tsv')
setchks_session.load_uploaded_data_into_matrix(data=fh, upload_method="from_text_file")
setchks_session.cid_col=0

print("=====================")
setchk.run_check(setchks_session=setchks_session)
print("=====================")

print("++++++++++++++++++++++++")
print(setchks_session)
print("++++++++++++++++++++++++")

print("++++++++++++++++++++++++")
for k,v in setchks_session.setchks_results.items(): 
    print("Results for check %s :" % k)
    print(v)
print("++++++++++++++++++++++++")


