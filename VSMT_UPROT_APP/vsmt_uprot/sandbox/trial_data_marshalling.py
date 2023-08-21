#!/usr/bin/env python
import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP/')

import vsmt_uprot.setchks.setchk_definitions 
from vsmt_uprot.setchks.setchks_session import SetchksSession
from vsmt_uprot.setchks.data_as_matrix.column_info import ColumnInfo
from vsmt_uprot.setchks.data_as_matrix.marshalled_row_data import MarshalledRow

from vsmt_uprot.terminology_server_module import TerminologyServer

setchks_session=SetchksSession()


fh=open('trial2.tsv')
setchks_session.load_data_into_matrix(data=fh, upload_method="from_text_file", table_has_header=True)
# setchks_session.cid_col=0

ci=ColumnInfo(ncols=len(setchks_session.data_as_matrix[0]))

ci.set_column_type(icol=0,requested_column_type="CID")
ci.set_column_type(icol=1,requested_column_type="DTERM")

print(ci)

mr=MarshalledRow(row_data=setchks_session.data_as_matrix[1], column_info=ci)
print(mr)