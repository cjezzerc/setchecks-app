#!/usr/bin/env python
import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP')

from vsmt_uprot.snomed_utils import parse_and_validate_sctid


for sctid in [  '819541000000103',
                '819541000000113',
                '819541000000123',
                '819541000000173',
                '81954103',
                '0819541000000103',
                '80103',
                '8888819541000000103',
                'SCT819541000000103',
                '819541000000103.0',
                ' 819541000000103',
                '819541000000103 ',
                '81954 1000000 10 3',

                ]:
    print(sctid)
    parse_and_validate_sctid(sctid)
    print("")

