from .setchk_results import SetchkResults


class CheckItem:
    """A class to hold information about one outcome of a check on a particular data row"""

    __slots__ = [
        "outcome_code",
        "general_message",
        "row_specific_message",
        "outcome_level",  # suggest "ISSUE" or "INFO" or "DEBUG"
    ]

    def __init__(self, outcome_code=None):
        self.outcome_code = outcome_code
        self.general_message = None
        self.row_specific_message = None
        self.outcome_level = (
            "ISSUE"  # defaults to "ISSUE"; only need to reset if e.g. "INFO"
        )
