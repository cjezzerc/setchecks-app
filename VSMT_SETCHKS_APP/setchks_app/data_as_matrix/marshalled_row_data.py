"""class to hold the important data from a row in a standard fashion"""

from setchks_app.descriptions_service import descriptions_service

"""
For details of the different cases inferring C_Id or C_Id_via_latest_release etc see https://nhsd-jira.digital.nhs.uk/browse/SIV-500
In particular for meanings of all codes like:
 	DID_NISR_DID_ILR_CID_ISR
(The above case means "DID was entered but is Not In the Selected Release; But the DID IS In Latest Release; The derived CID is in the Selected Release)
Other codes build up from 
CID 	Concept Id
DID 	Description Id
ISR 	In Selected Release
NISR 	Not In Selected Release
ILR 	(but) In Latest Release
NILR 	(and) Not IN Latest Release
SILR 	Selected (release) Is Latest Release

The last code here covers cases where the selected release is the latest release so cannot do the two separate checks.
This part of the code is required for CHK02 SNOMED CT Identifiers are in selected SNOMED CT release
This code is heavily dependent on the mongodb code. If the the ontoserver were to develop ability to handle Description Ids completely
then this could all be rewritten.
"""

ds=descriptions_service.DescriptionsService()

class MarshalledRow():
    __slots__=[
        "sctid_cell",
        "dterm_cell",
        "blank_row",
        "C_Id_entered",
        "D_Id_entered",
        "D_Term_entered",
        # all items below here depend on access to an SCT release and hence can only be fully done when sct_version available
        # could add functionality later to check against latest edition AS WELL but for now keep data specific to state of SCT at
        # selected release
        "C_Id_derived_from_D_Id_entered",   
        "D_Term_derived_from_D_Id_entered", 
        "D_Id_derived_from_C_Id_entered_and_D_Term_entered", 
        #    "congruence_of_C_Id_entered_and_D_Id_entered",
        "congruence_of_C_Id_entered_and_D_Term_entered", 
        "congruence_of_D_Id_entered_and_D_Term_entered", 
        "C_Id", # this will contain either an entered C_Id or if D_Id given then the implied C_Id  
        "C_Id_source", # either "ENTERED", "DERIVED" or None  
        "C_Id_why_none", # this will explain why C_Id is None; either "NOT_SET_YET", None, "BLANK_ENTRY", "INVALID_SCTID", "DID_NOT_IN_RELEASE"
        "C_Id_via_latest_release", # This is C_Id obtained by looking in latest release; if derived from a D_Id in latest release then *may* also be in selected release
        "C_Id_active", # TBI possibly
        "D_Id_active",
        "row_processable",
        "row_processable_message",
        ]

    def __init__(self, *, row_data=None, columns_info=None): # things in init are done with ignorance of sct_version
        self.sctid_cell=None
        self.dterm_cell=None
        self.C_Id_entered=None
        self.D_Id_entered=None
        self.D_Term_entered=None
        
        self.row_processable=False # this will be set to True only if certain conditions are met
        self.row_processable_message="processability messages not implemented yet"

        ci=columns_info

        self.blank_row=True
        for cell in row_data:
            if not cell.blank:
                self.blank_row=False
                break
        
        if ci.have_mixed_column:
            self.sctid_cell=row_data[ci.mixed_column]
            if self.sctid_cell.component_type in ["Concept_Id", "Description_Id"]:
                self.row_processable=True # may rescind this when try to convert??
                if self.sctid_cell.component_type == "Concept_Id":
                    self.C_Id_entered=self.sctid_cell.string
                else:
                    self.D_Id_entered=self.sctid_cell.string
        
        if ci.have_dterm_column:
            self.dterm_cell=row_data[ci.dterm_column]
            self.D_Term_entered=self.dterm_cell.string


    def do_things_dependent_on_SCT_release(self, setchks_session=None): # this part needs to be called once sct_version, before run checks
        
        # (re)initialize things in case this is being called a second time due to e.g. sct_version change
        self.C_Id_derived_from_D_Id_entered=None
        self.D_Term_derived_from_D_Id_entered=None
        self.D_Id_derived_from_C_Id_entered_and_D_Term_entered=None
        self.congruence_of_C_Id_entered_and_D_Term_entered=None
        self.congruence_of_D_Id_entered_and_D_Term_entered=None
        self.C_Id=None
        self.C_Id_source=None
        self.C_Id_why_none="NOT_SET_YET"
        self.C_Id_via_latest_release=None
        self.C_Id_active=None #TBI possibly
        self.D_Id_active=None
        ci=setchks_session.columns_info
        
        if self.sctid_cell.blank:
            self.C_Id_why_none="BLANK_ENTRY"
            return
        
        if not self.sctid_cell.valid:
            self.C_Id_why_none="INVALID_SCTID"
            return

        if self.C_Id_entered is not None:
            C_Id_data=ds.get_data_about_concept_id(
                concept_id=self.C_Id_entered, 
                sct_version=setchks_session.sct_version,
                )
            if C_Id_data!=[]: # so C_Id_entered exists in selected release
                self.C_Id=self.C_Id_entered
                self.C_Id_source="ENTERED"
            else:   # C_Id_entered is not in selected release
                    # really also need to check if selected release is actually the latest release here and deal wth that more efficiently
                if setchks_session.sct_version==setchks_session.available_sct_versions[0]: # if selected release is latest release
                    self.C_Id_why_none="CID_NISR_SRIL"
                else: # look in latest release
                    C_Id_data_latest=ds.get_data_about_concept_id(
                        concept_id=self.C_Id_entered, 
                        sct_version=setchks_session.available_sct_versions[0],
                        )
                    print("==>>>", C_Id_data_latest)
                    if C_Id_data_latest!=[]: # C_Id_entered is in latest release
                        self.C_Id_why_none="CID_NISR_CID_ILR"
                        self.C_Id_via_latest_release=self.C_Id_entered
                    else:                    # C_Id_entered is not in lateset release either
                        self.C_Id_why_none="CID_NISR_CID_NILR"

        else: 
            assert(self.D_Id_entered is not None)
            D_Id_data=ds.get_data_about_description_id(
                description_id=self.D_Id_entered, 
                sct_version=setchks_session.sct_version
                )
            if D_Id_data is not None: # D_Id_data is a single dict (as can have only one associated concept)
                self.C_Id_derived_from_D_Id_entered=D_Id_data["concept_id"]
                self.D_Id_active=D_Id_data["active_status"]
                self.D_Term_derived_from_D_Id_entered=D_Id_data["term"]
                self.C_Id=self.C_Id_derived_from_D_Id_entered
                self.C_Id_source="DERIVED"
                self.C_Id_why_none=None
                if self.D_Term_entered:
                    self.congruence_of_D_Id_entered_and_D_Term_entered=(D_Id_data["term"].lower()==self.D_Term_entered.lower())
            else: # see comment above about what if selected is the latest version
                if setchks_session.sct_version==setchks_session.available_sct_versions[0]: # if selected release is latest release
                    self.C_Id_why_none="DID_NISR_SRIL"
                else: # look in latest release
                    D_Id_data_latest=ds.get_data_about_description_id(
                        description_id=self.D_Id_entered, 
                        sct_version=setchks_session.available_sct_versions[0],
                        )
                    if D_Id_data_latest is not None:
                        self.C_Id_derived_from_D_Id_entered=D_Id_data_latest["concept_id"]
                        self.D_Id_active=D_Id_data_latest["active_status"]
                        self.D_Term_derived_from_D_Id_entered=D_Id_data_latest["term"]
                        self.C_Id_via_latest_release=self.C_Id_derived_from_D_Id_entered
                        C_Id_data=ds.get_data_about_concept_id(
                            concept_id=self.C_Id_derived_from_D_Id_entered, 
                            sct_version=setchks_session.sct_version,
                            )
                        if C_Id_data!=[]:
                            self.C_Id_why_none="DID_NISR_DID_ILR_CID_ISR"
                        else:
                            self.C_Id_why_none="DID_NISR_DID_ILR_CID_NISR"
                    else:
                        self.C_Id_why_none="DID_NISR_DID_NILR"
            
                # return # CHECK THIS!!!!!!!!!!!!!!!!
            
        if self.C_Id_entered and self.D_Term_entered:
            C_Id_data=ds.get_data_about_concept_id(concept_id=self.C_Id_entered, sct_version=setchks_session.sct_version)
            self.congruence_of_C_Id_entered_and_D_Term_entered=False
            for item in C_Id_data: # C_Id_data is a list of dicts (as can have several associated descriptions)
                if item["term"].lower()==self.D_Term_entered.lower(): # case significance TBI
                    self.congruence_of_C_Id_entered_and_D_Term_entered=True
                    self.D_Id_derived_from_C_Id_entered_and_D_Term_entered=item["desc_id"]
                    break

    def __str__(self):
        output_str="\n"
        for attribute in self.__slots__:
            output_str+="%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return(output_str)

   