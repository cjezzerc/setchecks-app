"""
This module instantiates a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier

"""

from .setchk import Setchk
from .individual_setchk_functions import CHK01_APPROP_SCTID
from .individual_setchk_functions import CHK02_IDS_IN_RELEASE
# from .individual_setchk_functions import CHK00_DUMMY_CHECK
# from .individual_setchk_functions import CHK04_INACTIVE_CODES
from .individual_setchk_functions import CHK06_DEF_EXCL_FILTER
from .individual_setchk_functions import CHK20_INCORR_FMT_SCTID

setchks={}


# there is a lot of repetition below so this can probably be generalised into a loop in due course
# once naming conventions in various parts of the code have bedded in

setchks['CHK01_APPROP_SCTID']=Setchk(
    setchk_code='CHK01_APPROP_SCTID',
    setchk_short_name='CHK01 Appropriate SNOMED CT identifiers for value set members', 
    setchk_function=CHK01_APPROP_SCTID.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )

setchks['CHK02_IDS_IN_RELEASE']=Setchk(
    setchk_code='CHK02_IDS_IN_RELEASE',
    setchk_short_name='CHK02 Identifiers are in selected the SNOMED CT release.', 
    setchk_function=CHK02_IDS_IN_RELEASE.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )

setchks['CHK06_DEF_EXCL_FILTER']=Setchk(
    setchk_code='CHK06_DEF_EXCL_FILTER', 
    setchk_short_name='CHK06 Inclusion of not recommended concepts', 
    setchk_function=CHK06_DEF_EXCL_FILTER.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    )
setchks['CHK20_INCORR_FMT_SCTID']=Setchk(
    setchk_code='CHK20_INCORR_FMT_SCTID',
    setchk_short_name='CHK20 Incorrectly formatted SNOMED CT identifiers', 
    setchk_function=CHK20_INCORR_FMT_SCTID.do_check,
    setchk_data_entry_extract_types=["ALL"],
    )