""" class definition for SetCHksSession """

import uuid

from ..excel import generate_excel_output
from setchks_app.data_as_matrix import load_data_into_matrix
import setchks_app.setchks.setchk_definitions


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

    __slots__=("uuid",
               "unparsed_data", # big and only needed on the confirm upload page
               "filename",
               "data_as_matrix", # big and only needed when populating marshalled rows
               "table_has_header", 
               "first_data_row",
               "columns_info",
               "marshalled_rows", # big and often needed
               "cid_col", 
               "did_col", 
               "mixed_col", 
               "setchks_results", # big; each (big) individual setchk needed during setchk and when constructing report
               "terminology_server",
               "available_sct_versions", 
               "sct_version",
               "available_setchks",
               "selected_setchks",
               "setchks_jobs_list",
               )

    def __init__(self, session=None):
        # self.uuid=str(uuid.uuid4())
        # self.uuid=session.sid
        self.uuid=None
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
        self.available_setchks=setchks_app.setchks.setchk_definitions.setchks
        self.selected_setchks=None
        self.setchks_jobs_list=None
    
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
        generate_excel_output.generate_excel_output(setchks_session=self, excel_filename=excel_filename, setchks_to_include=setchks_to_include)
        

