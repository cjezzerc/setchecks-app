#!/usr/bin/env python

"""
This is just the harness code now. Other code has been moved into refactor_core_code and refactor_core_functions 

Original code went through various iterations, from having the whole snmoed release in memeory (very fast but takes up a lot
of memory for the transitive closure aka descendants and ancestors
This version uses mongodb to store limited concept info, but including the crucial descendants and ancestors part

"""

import sys
import time

from pymongo import MongoClient

sys.path.append("/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_SETCHKS_APP")
sys.path.append("/cygdrive/c/Users/jeremy/GIT_NHSD/Value-Set/VSMT_UPROT_APP")
from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.set_refactoring.compare_original_and_refactored_valsets import compare_original_and_refactored_valsets

concepts=ConceptsDict(sct_version="20230510")
   
# valsets=valset_module.ValsetCollection()

# trial_SCT_RULE='<<25899002'
# trial_SCT_RULE='=6698000|=25899002|=208666006|=208662008|=208667002|=208663003'
# trial_SCT_RULE='=6698000|=25899002|=208666006|=208662008|=208667002'
# input_valset=valset_module.Valset(clause_set_string=trial_SCT_RULE, valset_name='input')

valset_extens_defn=[6698000,25899002,208666006,208662008,208667002,208663003]
# # input_valset=valset_module.Valset(valset_extens_defn=valset_extens_defn, valset_name='input')

# valsets.append(valset=input_valset)
# valset=valsets[valsets.valset_name_to_id['input']]
# print(valset)

print("\n\nSTARTING_REFACTOR:") 
start_time=time.time()

valsets=refactor_core_code.refactor_core_code(
    # clause_set_string=trial_SCT_RULE,
    valset_extens_defn=valset_extens_defn,
    concepts=concepts,
    )

elapsed_time=time.time()-start_time

compare_original_and_refactored_valsets(
    valsets=valsets, 
    concepts=concepts, 
    elapsed_time=elapsed_time,
    )

