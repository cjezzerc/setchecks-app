
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

    __slots__=("data_as_matrix", "table_has_header", "first_data_row", "cid_col", "did_col", "mixed_col", "setchks_results", "terminology_server", "sct_version")

    def __init__(self):
        self.data_as_matrix=[]
        self.table_has_header=None
        self.first_data_row=None
        self.cid_col=None
        self.did_col=None
        self.mixed_col=None
        self.setchks_results={}
        self.terminology_server=None
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
    
    def load_uploaded_data_into_matrix(self, data=None, upload_method=None, table_has_header=None, separator="\t"):
        self.table_has_header=table_has_header# True, False or None(==unknown)
        if self.table_has_header: # ** generally need graceful ways to cope with things like a file that has no data rows etc
            self.first_data_row=1
        else:
            self.first_data_row=0 
        if upload_method=="from_text_file":
            self.data_as_matrix=[]
            for line in data.readlines():
                if type(line)==str:
                    decoded_line=line
                else: # this seems to work if file data is passed from Flask app form POST
                    decoded_line=str(line, 'utf-8')
                f=decoded_line.split(separator)
                f=[x.strip() for x in f]
                self.data_as_matrix.append(f)


        

