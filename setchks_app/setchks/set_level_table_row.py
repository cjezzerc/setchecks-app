class SetLevelTableRow:
    """A class to hold information about one row set level output"""

    __slots__ = [
        "outcome_code",
        "simple_message",
        "descriptor",
        "value",
    ]

    def __init__(
        self,
        outcome_code=None,
        simple_message=None,
        descriptor=None,
        value=None,
    ):
        self.outcome_code = outcome_code
        self.simple_message = simple_message
        self.descriptor = descriptor
        self.value = value
