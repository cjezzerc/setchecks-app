"""
This module instantiates a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier

"""

from .setchk import Setchk
from .individual_setchk_functions import CHK00_DUMMY_CHECK
from .individual_setchk_functions import CHK04_INACTIVE_CODES
from .individual_setchk_functions import CHK06_DEF_EXCL_FILTER

setchks={}


# there is a lot of repetition below so this can probably be generalised into a loop in due course
# once naming conventions in various parts of the code have bedded in

setchks['CHK00_DUMMY_CHECK']=Setchk(setchk_name='CHK00_DUMMY_CHECK', setchk_function=CHK00_DUMMY_CHECK.do_check)
setchks['CHK04_INACTIVE_CODES']=Setchk(setchk_name='CHK04_INACTIVE_CODES', setchk_function=CHK04_INACTIVE_CODES.do_check)
setchks['CHK06_DEF_EXCL_FILTER']=Setchk(setchk_name='CHK06_DEF_EXCL_FILTER', setchk_function=CHK06_DEF_EXCL_FILTER.do_check)