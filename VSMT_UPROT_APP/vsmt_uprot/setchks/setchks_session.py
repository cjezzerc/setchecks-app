
from . import setchk_excel
from .data_as_matrix import load_data_into_matrix

class SetchksSession():
    """
    A class representing the full state of a session of checking a value set.

    This class will (provisionally) bundle all information during the process
    of running a set of checks againsta particular value set

    An instance of the class will contain (at least)
    * The value set data in raw 2D table form as supplied (TBC where source is FHIR)
    * Parameters such as
        * Which checks to run
        * SNOMED CT version
        * Whether data set is for data entry
    * Limited metadata about the valueset (for MI purposes)
    * The results of the individual checks
    * a means to execute the tests(via rq?), and (TBC) a means to monitor progress

    A session can equally well describe a GUI based session, or a check process 
    initiated from a script. In a webapp scenario the VsCheckSession object is
    envisaged to be held in a redis store and reloaded to service each request. If
    the instances become too large (e.g. when include results for very large value 
    sets) then redis process may need to be made to avoid loading the whole structure 
    every time.
    """

    __slots__=("unparsed_data",
               "filename",
               "data_as_matrix", 
               "table_has_header", 
               "first_data_row",
               "columns_info",
               "marshalled_rows", 
               "cid_col", 
               "did_col", 
               "mixed_col", 
               "setchks_results", 
               "terminology_server",
               "available_sct_versions", 
               "sct_version")

    def __init__(self):
        self.unparsed_data=None
        self.filename=None
        self.data_as_matrix=[]
        self.table_has_header=None
        self.first_data_row=None
        self.columns_info=None
        self.marshalled_rows=None
        self.cid_col=None
        self.did_col=None
        self.mixed_col=None
        self.setchks_results={}
        self.terminology_server=None
        self.available_sct_versions=None 
        self.sct_version=None
    
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
    
    def load_data_into_matrix(self, 
                                       data=None, 
                                       upload_method=None, 
                                       table_has_header=None, 
                                       separator="\t"):
        
        load_data_into_matrix.load_data_into_matrix(self, 
                                data=data, 
                                upload_method=upload_method, 
                                table_has_header=table_has_header, 
                                separator=separator)

    def generate_excel_output(self, excel_filename=None, setchks_to_include="ALL"):
        setchk_excel.generate_excel_output(setchks_session=self, excel_filename=excel_filename, setchks_to_include=setchks_to_include)
        

