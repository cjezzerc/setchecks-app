class SetLevelTableRow():
    """A class to hold information about one row of the tabular set level output
    """
    __slots__=[
        "descriptor",
        "value",
        ]

    def __init__(
        self, 
        descriptor=None, 
        value=None
        ):
        self.descriptor=descriptor
        self.value=value