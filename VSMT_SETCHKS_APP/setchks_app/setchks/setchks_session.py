""" class definition for SetchksSession """

import uuid

from ..excel import generate_excel_output
from setchks_app.data_as_matrix import load_data_into_matrix
from setchks_app.data_as_matrix import column_content_assessment
import setchks_app.setchks.setchk_definitions
from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.sct_versions import get_sct_versions



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
               "load_file_behaviour",
               "data_as_matrix", # big and only needed when populating marshalled rows
               "table_has_header", 
               "first_data_row",
               "columns_info",
               "data_entry_extract_type", # provisional allowed values "ENTRY_PRIMARY", "ENTRY_OTHER", "EXTRACT"
               "marshalled_rows", # big and often needed
               "column_content_assessment",
               "time_started_processing",
               "processing_status",
               "preprocessing_done",
               "preprocessing_failed",
               "passes_gatekeeper",
               "setchks_to_run_as_gatekeeper_not_passed",
               "setchks_results", # big; each (big) individual setchk needed during setchk and when constructing report
               "refactored_form",
               "terminology_server",
               "available_sct_versions", 
               "vs_name",
               "vs_purpose",
               "sct_version",
               "sct_version_b",
               "sct_version_mode",
               "available_setchks",
               "selected_setchks",
               "setchks_jobs_list",
               "setchks_jobs_manager",
               "setchks_run_status",
               "all_CHKXX_finished",
               "output_full_or_compact",
               "excel_filename",
               "excel_file_available",
               "excel_file_generation_failed",
               "timings",
               "app_version",
               )

    def __init__(self, session=None):
        # self.uuid=str(uuid.uuid4())
        # self.uuid=session.sid
        self.uuid=None
        self.unparsed_data=None
        self.filename=None
        self.load_file_behaviour="DEFAULT_SETTINGS"
        self.data_as_matrix=[]
        self.table_has_header=None
        self.first_data_row=None
        self.columns_info=None
        self.data_entry_extract_type="ENTRY_PRIMARY"
        self.marshalled_rows=None
        self.column_content_assessment=column_content_assessment.ColumnContentAssessment()
        self.time_started_processing=None
        self.processing_status="1_CHECKS_READY_TO_RUN" # strictly only the case if data loaded, sct_releases chosen etc
        self.preprocessing_done=False
        self.preprocessing_failed=False
        self.passes_gatekeeper=None
        self.setchks_to_run_as_gatekeeper_not_passed=[]
        self.setchks_results={}
        self.refactored_form=None
        self.terminology_server=None
        self.available_sct_versions=None # see initialise below
        self.vs_name=""
        self.vs_purpose=""
        self.sct_version=None # see initialise below
        self.sct_version_b=None # see initialise below
        self.sct_version_mode="SINGLE_SCT_VERSION"
        self.available_setchks=setchks_app.setchks.setchk_definitions.setchks
        self.selected_setchks=None
        self.setchks_jobs_list=None
        self.setchks_jobs_manager=None
        self.setchks_run_status={}
        self.all_CHKXX_finished=False
        self.output_full_or_compact="COMPACT_OUTPUT"
        self.excel_filename=None
        self.excel_file_available=False
        self.excel_file_generation_failed=False
        self.timings={} # arbitrary entries can be put in this dict for debug purposes
        self.app_version="FUNCTIONALITY_DISABLED" # current_app.config["VERSION"] # need way to do this differently if not run from app
        self.initialise_sct_versions()
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

    def generate_excel_output(self, setchks_to_include="ALL"):
        return generate_excel_output.generate_excel_output(
            setchks_session=self, 
            excel_filename=self.excel_filename, 
            setchks_to_include=setchks_to_include
            )
        
    def reset_analysis(self): # this should be called whenever a change is made 
                              # (e.g. choice of sct release or data_entry_extract_type)
                              # that renders analyses done invalid
        self.setchks_results={}
        self.refactored_form=None
        self.setchks_run_status={}
        self.setchks_jobs_manager=None
        self.excel_file_available=False
        self.excel_file_generation_failed=False
        self.time_started_processing=None
        self.preprocessing_done=False
        self.preprocessing_failed=False
        self.passes_gatekeeper=None
        self.setchks_to_run_as_gatekeeper_not_passed=[]
        self.all_CHKXX_finished=False
        self.processing_status="1_CHECKS_READY_TO_RUN" # strictly only the case if data loaded, sct_releases chosen etc

    def initialise_sct_versions(self):
        all_available_sct_versions={x.date_string: x for x in get_sct_versions.get_sct_versions()}
        self.available_sct_versions=[]
        ds=DescriptionsService(data_type="hst")
        hst_dict=ds.check_whether_releases_on_ontoserver_have_collections()
        for sct_version, hst_exists in hst_dict.items():
            if hst_exists: # only make sct_version available if has an HST 
                self.available_sct_versions.append(all_available_sct_versions[sct_version])

        self.sct_version=self.available_sct_versions[0]
        self.sct_version_b=self.available_sct_versions[0]

    def do_SCT_release_dependent_preprocessing(self):
        self.passes_gatekeeper=True
        for mr in self.marshalled_rows:
            mr.do_things_dependent_on_SCT_release(setchks_session=self)
            if self.passes_gatekeeper:
                if mr.C_Id is None and not mr.blank_row:
                    self.passes_gatekeeper=False
                elif self.data_entry_extract_type=="EXTRACT" and mr.D_Id_entered is not None:
                    self.passes_gatekeeper=False
        self.preprocessing_done=True
        return self.marshalled_rows, self.preprocessing_done , self.passes_gatekeeper # this is for if run in a queue
        # return self # this is for if run in a queue
