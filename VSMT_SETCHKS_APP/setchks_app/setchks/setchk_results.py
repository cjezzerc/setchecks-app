class SetchkResults():
    """
    A class used to represent the results of a particular check on a particular value set.

    When the check implied by a Setchk object is run in the context of a particular
    SetchksSession then it will generate a SetchkResults object that will be stored
    in the SetchksSession structure

    Provisionally this class will hold 
        * a standard set of structures that hold results in a way that a standard reporting 
        tool can handle
        * ad hoc extra structures as needs arise (that the corresponding Setchk object 
        can provide methods to represent)
        * the standard structures need to be at row, set and concept level (as a first stab) 
    """
    
    __slots__=(
        "row_analysis", 
        "set_analysis", 
        "set_level_table_rows",
        "concept_analysis", 
        "setchk_code", 
        "meta_data",
        "supp_tab_headers",
        "supp_tab_blocks",
        "chk_specific_sheet"
        )

    def __init__(self):

        self.row_analysis=[]
        self.set_analysis={}
        self.set_level_table_rows=[]
        self.concept_analysis={}
        self.setchk_code={}
        self.meta_data={}
        self.supp_tab_headers=None
        self.supp_tab_blocks=None
        self.chk_specific_sheet=None

    def __repr__(self):
        repr_strings=[]
        # for k,v in self.__dict__.items():
        for k in self.__slots__:
            v=self.__getattribute__(k)
            if type(v) in (list, set) and len(v)>20:
                repr_strings.append("%20s : %s of %s elements" % (k, type(v), len(v)))
            elif type(v) in (dict,) and len(v)>20:
                repr_strings.append("%20s : %s with %s elements" % (k, type(v), len(v)))
            else:
                repr_strings.append("%20s : %s (%s)" % (k,v,type(v)))
        return "\n".join(repr_strings)