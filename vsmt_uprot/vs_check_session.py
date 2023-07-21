
class VsCheckSession():
    def __init__(self):
        self.data_as_matrix=[]
    
    def __repr__(self):
        repr_strings=[]
        for k,v in self.__dict__.items():
            if type(v) in (list, set) and len(v)>20:
                repr_strings.append("%20s : %s of %s elements" % (k, type(v), len(v)))
            else:
                repr_strings.append("%20s : %s (%s)" % (k,v,type(v)))
        return "\n".join(repr_strings)
    
    def load_uploaded_data_into_matrix(self, data=None, upload_method=None, separator="\t"):
        if upload_method=="from_text_file":
            self.data_as_matrix=[]
            for line in data.readlines():
                f=str(line, 'utf-8').split(separator)
                f=[x.strip() for x in f]
                self.data_as_matrix.append(f)

        

