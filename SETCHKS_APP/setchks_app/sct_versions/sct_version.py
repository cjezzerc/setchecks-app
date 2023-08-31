""" class definition for object to hold information about an sct version """

class SctVersion():
    __slots__=  [   "formal_version_string", 
                    "date_string_for_sorting",
                    "name_for_pulldown",
                    "version_detail",
                ]   
              
    def __init__(self, formal_version_string=None):
        self.formal_version_string=formal_version_string
        self.date_string_for_sorting=self.formal_version_string.split("/")[-1]
        self.name_for_pulldown="UK Monolith edition : %s" % self.date_string_for_sorting
        self.version_detail=None