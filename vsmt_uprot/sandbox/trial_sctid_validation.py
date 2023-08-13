#!/usr/bin/env python
import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/')

from vsmt_uprot.snomed_utils import parse_and_validate_sctid

parse_and_validate_sctid('819541000000103')
parse_and_validate_sctid('81954103')
parse_and_validate_sctid('0819541000000103')
parse_and_validate_sctid('80103')
parse_and_validate_sctid('8888819541000000103')
parse_and_validate_sctid('SCT819541000000103')
parse_and_validate_sctid('819541000000103.0')
parse_and_validate_sctid(' 819541000000103')
parse_and_validate_sctid('819541000000103 ')
parse_and_validate_sctid('81954 1000000 10 3')

