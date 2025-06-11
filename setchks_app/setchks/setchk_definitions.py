"""
This module instantiates a configured set of Setchk objects

The structure provided is a dictionary of Setchk objects keyed by the
check's long identifier

"""

from .setchk import Setchk
from .individual_setchk_functions import CHK01_APPROP_SCTID
from .individual_setchk_functions import CHK02_IDS_IN_RELEASE
from .individual_setchk_functions import CHK03_TERM_CONGRUENCE
from .individual_setchk_functions import CHK04_INACTIVES_ENTRY
from .individual_setchk_functions import CHK05_UNRECC_HIERARCH
from .individual_setchk_functions import CHK06_DEF_EXCL_FILTER
from .individual_setchk_functions import CHK08_IMPLIED_INACTIVES
from .individual_setchk_functions import CHK10_MISSING_CONCEPTS
from .individual_setchk_functions import CHK12_MIXED_TAGS
from .individual_setchk_functions import CHK14_MANY_CLAUSES
from .individual_setchk_functions import CHK20_INCORR_FMT_SCTID
from .individual_setchk_functions import CHK22_DUPLICATE_REFS
from .individual_setchk_functions import CHK51_SUGGESTS_DUAL_SCT

setchks = {}


# there is a lot of repetition below so this can probably be generalised into a loop in due course
# once naming conventions in various parts of the code have bedded in

setchks["CHK01_APPROP_SCTID"] = Setchk(
    setchk_code="CHK01_APPROP_SCTID",
    setchk_short_name="ID type checks",
    setchk_function=CHK01_APPROP_SCTID.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK02_IDS_IN_RELEASE"] = Setchk(
    setchk_code="CHK02_IDS_IN_RELEASE",
    setchk_short_name="IDs found in selected release",
    setchk_function=CHK02_IDS_IN_RELEASE.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION", "DUAL_SCT_VERSIONS"],
)


setchks["CHK03_TERM_CONGRUENCE"] = Setchk(
    setchk_code="CHK03_TERM_CONGRUENCE",
    setchk_short_name="Appropriate / consistent Terms",
    setchk_function=CHK03_TERM_CONGRUENCE.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK04_INACTIVES_ENTRY"] = Setchk(
    setchk_code="CHK04_INACTIVES_ENTRY",
    setchk_short_name="Inactive Concepts",
    setchk_function=CHK04_INACTIVES_ENTRY.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION", "DUAL_SCT_VERSIONS"],
)

setchks["CHK05_UNRECC_HIERARCH"] = Setchk(
    setchk_code="CHK05_UNRECC_HIERARCH",
    setchk_short_name="Acceptable hierarchies",
    setchk_function=CHK05_UNRECC_HIERARCH.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK06_DEF_EXCL_FILTER"] = Setchk(
    setchk_code="CHK06_DEF_EXCL_FILTER",
    setchk_short_name="Default Exclusion RefSet",
    setchk_function=CHK06_DEF_EXCL_FILTER.do_check,
    setchk_data_entry_extract_types=["ENTRY_PRIMARY", "ENTRY_OTHER"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK08_IMPLIED_INACTIVES"] = Setchk(
    setchk_code="CHK08_IMPLIED_INACTIVES",
    setchk_short_name="Suggestions for inactive predecessors",
    setchk_function=CHK08_IMPLIED_INACTIVES.do_check,
    setchk_data_entry_extract_types=["EXTRACT"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK10_MISSING_CONCEPTS"] = Setchk(
    setchk_code="CHK10_MISSING_CONCEPTS",
    setchk_short_name="Suggestions for missing content",
    setchk_function=CHK10_MISSING_CONCEPTS.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
    setchk_set_level_only=True,
)

setchks["CHK12_MIXED_TAGS"] = Setchk(
    setchk_code="CHK12_MIXED_TAGS",
    setchk_short_name="Mixed Semantic Tags",
    setchk_function=CHK12_MIXED_TAGS.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)


setchks["CHK14_MANY_CLAUSES"] = Setchk(
    setchk_code="CHK14_MANY_CLAUSES",
    setchk_short_name="Complexity analysis",
    setchk_function=CHK14_MANY_CLAUSES.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
    setchk_set_level_only=True,
)

setchks["CHK20_INCORR_FMT_SCTID"] = Setchk(
    setchk_code="CHK20_INCORR_FMT_SCTID",
    setchk_short_name="IDs have correct format",
    setchk_function=CHK20_INCORR_FMT_SCTID.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION", "DUAL_SCT_VERSIONS"],
)

setchks["CHK22_DUPLICATE_REFS"] = Setchk(
    setchk_code="CHK22_DUPLICATE_REFS",
    setchk_short_name="Duplicate entries",
    setchk_function=CHK22_DUPLICATE_REFS.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["SINGLE_SCT_VERSION"],
)

setchks["CHK51_SUGGESTS_DUAL_SCT"] = Setchk(
    setchk_code="CHK51_SUGGESTS_DUAL_SCT",
    setchk_short_name="Release version set differences",
    setchk_function=CHK51_SUGGESTS_DUAL_SCT.do_check,
    setchk_data_entry_extract_types=["ALL"],
    setchk_sct_version_modes=["DUAL_SCT_VERSIONS"],
    setchk_set_level_only=True,
)
