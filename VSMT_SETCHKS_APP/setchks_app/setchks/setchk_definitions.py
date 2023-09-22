"""
This module instantiates a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier

"""

from .setchk import Setchk
from .individual_setchk_functions import CHK01_APPROP_SCTID
# from .individual_setchk_functions import CHK00_DUMMY_CHECK
# from .individual_setchk_functions import CHK04_INACTIVE_CODES
from .individual_setchk_functions import CHK06_DEF_EXCL_FILTER
from .individual_setchk_functions import CHK20_INCORR_FMT_SCTID

setchks={}


# there is a lot of repetition below so this can probably be generalised into a loop in due course
# once naming conventions in various parts of the code have bedded in

setchks['CHK01_APPROP_SCTID']=Setchk(
    setchk_code='CHK01_APPROP_SCTID',
    setchk_short_name='Appropriate SNOMED CT identifiers for value set members', 
    setchk_function=CHK01_APPROP_SCTID.do_check,
    )
# setchks['CHK00_DUMMY_CHECK']=Setchk(
#     setchk_code='CHK00_DUMMY_CHECK', 
#     setchk_short_name='early_trial_CHK00_DUMMY_CHECK', 
#     setchk_function=CHK00_DUMMY_CHECK.do_check,
#     )
# setchks['CHK04_INACTIVE_CODES']=Setchk(
#     setchk_code='CHK04_INACTIVE_CODES', 
#     setchk_short_name='early_trial_CHK04_INACTIVE_CODES', 
#     setchk_function=CHK04_INACTIVE_CODES.do_check,
#     )
setchks['CHK06_DEF_EXCL_FILTER']=Setchk(
    setchk_code='CHK06_DEF_EXCL_FILTER', 
    setchk_short_name='Inclusion of not recommended concepts', 
    setchk_function=CHK06_DEF_EXCL_FILTER.do_check,
    )
setchks['CHK20_INCORR_FMT_SCTID']=Setchk(
    setchk_code='CHK20_INCORR_FMT_SCTID',
    setchk_short_name='Incorrectly formatted SNOMED CT identifiers', 
    setchk_function=CHK20_INCORR_FMT_SCTID.do_check,
    )