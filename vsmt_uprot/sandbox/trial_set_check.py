#!/usr/bin/env python
import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/')

import vsmt_uprot.setchks.setchk_definitions 
from vsmt_uprot.setchks.setchks_session import SetchksSession
from vsmt_uprot.terminology_server_module import TerminologyServer

setchks_session=SetchksSession()

setchks_session.terminology_server=TerminologyServer(base_url=os.environ["ONTOSERVER_INSTANCE"],
                                     auth_url=os.environ["ONTOAUTH_INSTANCE"])
release_label="20230412"
setchks_session.sct_version="http://snomed.info/sct/83821000000107/version/" + release_label

fh=open('trial1.tsv')
setchks_session.load_uploaded_data_into_matrix(data=fh, upload_method="from_text_file", table_has_header=True)
setchks_session.cid_col=0


for setchk_name in ['CHK00_DUMMY_CHECK','CHK06_DEF_EXCL_FILTER']:
    
    setchk=vsmt_uprot.setchks.setchk_definitions.setchks[setchk_name]

    print("=====================")
    setchk.run_check(setchks_session=setchks_session)
    print("=====================")

    print("++++++++++++++++++++++++")
    print("After set check ran, setchks_sessions is:")
    print(setchks_session)
    print("++++++++++++++++++++++++")

    print("++++++++++++++++++++++++")
    for k,v in setchks_session.setchks_results.items(): 
        print("Results for check %s :" % k)
        print(v)
    print("++++++++++++++++++++++++")

setchks_session.generate_excel_output(excel_filename='/tmp/setchks_output.xlsx')



