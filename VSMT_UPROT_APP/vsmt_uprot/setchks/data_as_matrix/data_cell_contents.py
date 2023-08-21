"""class to hold contents of a data cell once it has been parsed etc"""

from vsmt_uprot.snomed_utils import ParsedSCTID

class DataCellContents():
    __slots__=["parsed_sctid", "cell_column_type_consistency"]
    def __init__(self, cell_contents=None):
        self.parsed_sctid=ParsedSCTID(string=cell_contents)
        self.cell_column_type_consistency=None
    
    def __str__(self):
        output_str=""
        for attribute in self.__slots__:
            output_str+="%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return(output_str)

    def __repr__(self):
        cell_contents_string=self.parsed_sctid.sctid_string
        is_a_valid_sctid=self.parsed_sctid.valid
        component_type=self.parsed_sctid.component_type
        repr_string="DataCellContents (%s,%s,%s)" % (cell_contents_string,
                                                     is_a_valid_sctid,
                                                     component_type)
        return repr_string
    
    @property
    def string(self):
        return self.parsed_sctid.sctid_string
    
    @property
    def component_type(self):
        return self.parsed_sctid.component_type