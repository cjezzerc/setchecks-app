"""
This module provides a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier
"""

from .setchk import Setchk
from .individual_setchk_functions import a_test_check

setchks={}

setchks['a_test_check']=Setchk(setchk_name='a_test_check', setchk_function=a_test_check.do_check)