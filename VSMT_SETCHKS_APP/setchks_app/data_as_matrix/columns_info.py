"""class to hold the important data from a row in a standard fashion"""

import copy

class ColumnsInfo():
    __slots__=["_identified_columns",   # dict of the columns nominated as providing particular info
               "_column_types", # list of types of each column; possible values="CID","DID","MIXED","DTERM","OTHER"
                "_ncols"
                ]

# allowed combos = CID  ;   DID   ; MIXED  ; CID and DID

    def __init__(self, ncols):
        self._identified_columns={"CID":None,
                                 "DID":None,
                                 "MIXED":None,
                                 "DTERM":None,                    
                                 }
        self._ncols=ncols
        self._column_types=["OTHER"]*self._ncols
    
    def __str__(self):
        output_str="\n"
        for attribute in self.__slots__:
            output_str+="%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return(output_str)
    
    def set_column_type(self, *, icol=None, requested_column_type=None):
        
        if requested_column_type not in ["CID","DID","MIXED","DTERM","OTHER"]:
            return(False,"FAIL: Illegal column type requested")
        
        current_type=self._column_types[icol]
        
        if requested_column_type==current_type:
            return(True,"SUCCESS: No change requested")
        
        if requested_column_type=="OTHER":
            self._column_types[icol]="OTHER"
            if current_type in ["CID","DID","MIXED","DTERM"]:
                self._identified_columns[current_type]=None
            return(True, "SUCCESS: Changed to OTHER")   
        
        if self._identified_columns[requested_column_type] is not None:
            return False,"FAIL: Another column is already identified as that type; change that one first"
        
        # else, see if the combination after the change were made would be legal
        trial_identified_columns=copy.deepcopy(self._identified_columns)
        trial_identified_columns[current_type]=None 
        trial_identified_columns[requested_column_type]=icol 
        test_tuple=(trial_identified_columns["CID"]!=None, 
                    trial_identified_columns["DID"]!=None, 
                    trial_identified_columns["MIXED"]!=None)
        if test_tuple in [(False,False,False),   # nothing selected
                          (True ,False,False),   # just CID
                          (False,True ,False),   # just DID
                          (True ,True ,False),   # CID and DID
                          (False,False,True )]:   # Just MIXED
            self._identified_columns[current_type]=None
            self._identified_columns[requested_column_type]=icol
            self._column_types[icol]=requested_column_type
            return True, "SUCCESS: Changed OK" 
        else:
            return False, "FAIL: The resulting set of identified columns is illegal" +str(test_tuple)

    @property
    def ncols(self):
        return self._ncols

    @property
    def column_types(self):
        return self._column_types
    
    @property
    def identified_columns(self):
        return self._identified_columns

    @property
    def identification_sufficient(self):
        test_tuple=(self._identified_columns["CID"]!=None, 
                    self._identified_columns["DID"]!=None, 
                    self._identified_columns["MIXED"]!=None)
        if test_tuple in [(True ,False,False),   # just CID
                          (False,True ,False),   # just DID
                          (True ,True ,False),   # CID and DID
                          (False,False,True )]:   # Just MIXED
            return True
        else:
            return False
        
    @property
    def cid_column(self):
        return self._identified_columns["CID"]
    
    @property
    def did_column(self):
        return self._identified_columns["DID"]
    
    @property
    def mixed_column(self):
        return self._identified_columns["MIXED"]
    
    @property
    def dterm_column(self):
        return self._identified_columns["DTERM"]
    
    @property
    def have_cid_column(self):
        test=(self._identified_columns["CID"]!=None)
        return (test)

    @property
    def have_did_column(self):
        test=(self._identified_columns["DID"]!=None)
        return (test)
    
    @property
    def have_mixed_column(self):
        test=(self._identified_columns["MIXED"]!=None)
        return (test)
    
    @property
    def have_dterm_column(self):
        test=(self._identified_columns["DTERM"]!=None)
        return (test)

    @property
    def have_just_cid_column(self):
        test=(self._identified_columns["CID"]!=None) and (self._identified_columns["DID"]==None)
        return (test)
    
    @property
    def have_just_did_column(self):
        test=(self._identified_columns["CID"]==None) and (self._identified_columns["DID"]!=None)
        return (test)

    @property
    def have_both_cid_and_did_columns(self):
        test=(self._identified_columns["CID"]!=None) and (self._identified_columns["DID"]!=None)
        return (test)
    
    @property
    def have_mixed_column(self):
        test=(self._identified_columns["MIXED"]!=None)
        return (test)


if __name__=="__main__":
    ci=ColumnInfo(7)
    print(ci)
    for actions in [    [3,"OTHER",True],
                        [3,"CID",True],
                        [3,"DID", True],
                        [2,"DID", False],
                        [2,"CID", True],
                        [4,"MIXED", False],
                        [2,"OTHER", True],
                        [3,"OTHER", True],
                        [4,"MIXED", True],
                        [2,"CID", False],
                        [1,"DTERM", True],
                        [6,"DTERM", False],
                        [1,"OTHER", True],
                        [6,"DTERM", True],
                        [6,"OTHER", True],
                        [4,"DTERM", True],
                        [4,"JELLY", False],
                    ]:
        expected_outcome=actions[2]
        success, message=ci.set_column_type(icol=actions[0], requested_column_type=actions[1])
        print("Actions:", actions)
        print("Success:", success)
        print("Message:", message)
        print(ci)
        print(ci.cid_column, ci.did_column, ci.mixed_column, ci.dterm_column)
        print(ci.have_just_cid_column, ci.have_just_did_column, ci.have_both_cid_and_did_columns, ci.have_mixed_column, ci.have_dterm_column)
        print("Identification sufficient:", ci.identification_sufficient)
        print("--> Passes test: %s" % (success==expected_outcome))
        print("============================")
    
                    