"""class to hold the important data from a row in a standard fashion"""



class MarshalledRow():
    __slots__=["cell",
            #    "C_Id_entered",
            #    "D_Id_entered",
            #    "D_Term_entered",
            #    "C_id_derived_from_D_Id_entered",
            #    "D_Term_derived_from_D_Id_entered",
            #    "D_Id_derived_from_C_Id_entered_and_D_Term_entered",
            #    "congruence_of_C_Id_entered_and_D_Id_entered",
            #    "congruence_of_C_Id_entered_and_D_Term_entered",
            #    "congruence_of_D_Id_entered_and_D_Term_entered",
               "row_processable",
               "row_processable_message"]
    # May want to add source of C_Id_entered and D_Id_entered ??

    def __init__(self, *, row_data=None, columns_info=None): # things in init are done with ignorance of sct_version
        self.cell=None
        # self.C_Id_entered=None
        # self.D_Id_entered=None
        # self.D_Term_entered=None
        # self.C_id_derived_from_D_Id_entered=None
        # self.D_Term_derived_from_D_Id_entered=None
        # self.D_Id_derived_from_C_Id_entered_and_D_Term_entered=None
        # self.congruence_of_C_Id_entered_and_D_Id_entered=None
        # self.congruence_of_C_Id_entered_and_D_Term_entered=None
        # self.congruence_of_D_Id_entered_and_D_Term_entered=None
        self.row_processable=False
        self.row_processable_message="processability messages not implemented yet"

        ########## decide if row is processable ##########
        ########## very basic inflexible rules for now  ##

        ci=columns_info
        # cid_col_cpt_type=None
        # if ci.have_cid_column:
        #     cid_col_cpt_type=row_data[ci.cid_column].component_type
        
        # did_col_cpt_type=None
        # if ci.have_did_column:
        #     did_col_cpt_type=row_data[ci.did_column].component_type
        
        if ci.have_mixed_column:
            self.cell=row_data[ci.mixed_column]
            if self.cell.component_type in ["Concept_Id", "Description_Id"]:
                self.row_processable=True # probably rescind this when try to convert??

        # if ci.have_just_cid_column:
        #     if cid_col_cpt_type=="Concept_Id":
        #         self.row_processable=True
        
        # if ci.have_just_did_column:
        #     if did_col_cpt_type=="Description_Id":
        #         self.row_processable=True
        
        # if ci.have_both_cid_and_did_columns:
        #     if (cid_col_cpt_type=="Concept_Id") and (did_col_cpt_type=="Description_Id"):
        #         self.row_processable=True

        # if ci.have_mixed_column:
        #     if mixed_col_cpt_type in ["Concept_Id", "Description_Id"]:
        #         self.row_processable=True
        #     if mixed_

        # if ci.have_cid_column:
        #     self.C_Id_entered=row_data[ci.cid_column]
            
        # if ci.have_did_column:
        #     self.D_Id_entered=row_data[ci.did_column]

        # if ci.have_dterm_column:
        #     self.D_Term_entered=row_data[ci.dterm_column]

    def get_implied_concept_ids_ETC_ETC(self, setchks_session=None): # this part needs to be called once sct_version, before run checks
        ci=setchks_session.columns_info

        pass
        # mixed_col_cpt_type=row_data[ci.mixed_column].component_type

    def __str__(self):
        output_str="\n"
        for attribute in self.__slots__:
            output_str+="%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return(output_str)

   