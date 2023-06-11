#!/usr/bin/env python

import sys, os

sys.path.append('/cygdrive/c/Users/jeremy/GIT/snomed_python/')
import release_processing

##############################
# Load SNOMED-CT from pickle #
##############################

branch_tag="UKCL_v36.0"

concepts=release_processing.read_concepts_pickle_file(branch_tag=branch_tag, verbose=True)

print(list(concepts.items())[0:10])