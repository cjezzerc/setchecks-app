"""class to hold the important data from a row in a standard fashion"""

from setchks_app.descriptions_service import descriptions_service
from setchks_app.sctid.restore_corrupted_id import detect_corruption_and_restore_id

import logging

logger = logging.getLogger(__name__)

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
SRIL 	Selected (release) Is Latest Release

The last code here covers cases where the selected release is the latest release so cannot do the two separate checks.
This part of the code is required for CHK02 SNOMED CT Identifiers are in selected SNOMED CT release
This code is heavily dependent on the mongodb code. If the the ontoserver were to develop ability to handle Description Ids completely
then this could all be rewritten.
"""

csr_indicators = {  # these abbreviations as in the SNOMED confluence pages
    "900000000000020002": "cI",
    "900000000000448009": "ci",
    "900000000000017005": "CS",
}

csr_terms = {
    "900000000000020002": "Only initial character case insensitive",
    "900000000000448009": "Entire term case insensitive",
    "900000000000017005": "Entire term case sensitive",
}


def compare_strings_csr(
    string1=None, string2=None, csr_SCT_code=None, csr_indicator=None
):
    # applies case significance rules
    # if csr_indicator not given, then csr_SCT_code must be given (and no checking of this done)
    # no checking for illegal code or very short strings implemented
    if csr_indicator is None:
        csr_indicator = csr_indicators[csr_SCT_code]
    # print(f"string1:{string1} {csr_indicator}")
    if csr_indicator == "ci":
        return string1.lower() == string2.lower()
    elif csr_indicator == "cI":
        return (string1[0].lower() == string2[0].lower()) and (
            string1[1:] == string2[1:]
        )
    else:
        return string1 == string2


ds = descriptions_service.DescriptionsService()


class MarshalledRow:

    __slots__ = [
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
        "D_Term_Type_derived_from_D_Id_entered",
        "D_Term_Type_derived_from_C_Id_entered_and_D_Term_entered",
        #    "congruence_of_C_Id_entered_and_D_Id_entered",
        "congruence_of_C_Id_entered_and_D_Term_entered_case_insens",
        "congruence_of_D_Id_entered_and_D_Term_entered_case_insens",
        "congruence_of_C_Id_entered_and_D_Term_entered_csr",
        "congruence_of_D_Id_entered_and_D_Term_entered_csr",
        "D_Term_csr_correct_derived_from_C_Id_entered_and_D_Term_entered",
        "C_Id",  # this will contain either an entered C_Id or if D_Id given then the implied C_Id
        "C_Id_source",  # either "ENTERED", "DERIVED" or None
        "C_Id_why_none",  # this will explain why C_Id is None; either "NOT_SET_YET", None, "BLANK_ENTRY", "INVALID_SCTID", "CID_NISR_SRIL", etc
        "C_Id_via_latest_release",  # This is C_Id obtained by looking in latest release; if derived from a D_Id in latest release then *may* also be in selected release
        "C_Id_active",  # TBI possibly
        "D_Id_active",
        "excel_corruption_suspected",
        "possible_reconstructed_C_Id",
        "possible_reconstructed_D_Id",
        "row_processable",
        "row_processable_message",
    ]

    def __init__(
        self, *, row_data=None, columns_info=None
    ):  # things in init are done with ignorance of sct_version
        self.sctid_cell = None
        self.dterm_cell = None
        self.C_Id_entered = None
        self.D_Id_entered = None
        self.D_Term_entered = None

        self.row_processable = (
            False  # this will be set to True only if certain conditions are met
        )
        self.row_processable_message = "processability messages not implemented yet"

        ci = columns_info

        self.blank_row = True
        for cell in row_data:
            if not cell.blank:
                self.blank_row = False
                break

        if ci.have_mixed_column:
            self.sctid_cell = row_data[ci.mixed_column]
            if self.sctid_cell.component_type in ["Concept_Id", "Description_Id"]:
                self.row_processable = True  # may rescind this when try to convert??
                if self.sctid_cell.component_type == "Concept_Id":
                    self.C_Id_entered = self.sctid_cell.string
                else:
                    self.D_Id_entered = self.sctid_cell.string

        if ci.have_dterm_column:
            self.dterm_cell = row_data[ci.dterm_column]
            self.D_Term_entered = self.dterm_cell.string

    def do_things_dependent_on_SCT_release(
        self, setchks_session=None
    ):  # this part needs to be called once sct_version, before run checks

        # (re)initialize things in case this is being called a second time due to e.g. sct_version change
        self.C_Id_derived_from_D_Id_entered = None
        self.D_Term_derived_from_D_Id_entered = None
        self.D_Id_derived_from_C_Id_entered_and_D_Term_entered = None
        self.D_Term_Type_derived_from_D_Id_entered = None
        self.D_Term_Type_derived_from_C_Id_entered_and_D_Term_entered = None
        self.congruence_of_C_Id_entered_and_D_Term_entered_case_insens = None
        self.congruence_of_D_Id_entered_and_D_Term_entered_case_insens = None
        self.congruence_of_C_Id_entered_and_D_Term_entered_csr = None
        self.congruence_of_D_Id_entered_and_D_Term_entered_csr = None
        self.D_Term_csr_correct_derived_from_C_Id_entered_and_D_Term_entered = None
        self.C_Id = None
        self.C_Id_source = None
        self.C_Id_why_none = "NOT_SET_YET"
        self.C_Id_via_latest_release = None
        self.C_Id_active = None  # TBI possibly
        self.D_Id_active = None
        self.excel_corruption_suspected = None
        self.possible_reconstructed_C_Id = None
        self.possible_reconstructed_D_Id = None
        ci = setchks_session.columns_info

        valid_SCTID = True
        if self.sctid_cell.blank:
            self.C_Id_why_none = "BLANK_ENTRY"
            valid_SCTID = False

        if not self.sctid_cell.valid:
            self.C_Id_why_none = "INVALID_SCTID"
            valid_SCTID = False

        if valid_SCTID:
            if self.C_Id_entered is not None:
                C_Id_data = ds.get_data_about_concept_id(
                    concept_id=self.C_Id_entered,
                    sct_version=setchks_session.sct_version,
                )
                if C_Id_data != []:  # so C_Id_entered exists in selected release
                    self.C_Id = self.C_Id_entered
                    self.C_Id_source = "ENTERED"
                else:  # C_Id_entered is not in selected release
                    if (
                        setchks_session.sct_version
                        == setchks_session.available_sct_versions[0]
                    ):  # if selected release is latest release
                        self.C_Id_why_none = "CID_NISR_SRIL"
                    else:  # look in latest release
                        C_Id_data_latest = ds.get_data_about_concept_id(
                            concept_id=self.C_Id_entered,
                            sct_version=setchks_session.available_sct_versions[0],
                        )
                        # print("==>>>", C_Id_data_latest)
                        if C_Id_data_latest != []:  # C_Id_entered is in latest release
                            self.C_Id_why_none = "CID_NISR_CID_ILR"
                            self.C_Id_via_latest_release = self.C_Id_entered
                        else:  # C_Id_entered is not in lateset release either
                            self.C_Id_why_none = "CID_NISR_CID_NILR"

            else:
                assert self.D_Id_entered is not None
                D_Id_data = ds.get_data_about_description_id(
                    description_id=self.D_Id_entered,
                    sct_version=setchks_session.sct_version,
                )
                if (
                    D_Id_data is not None
                ):  # D_Id_data is a single dict (as can have only one associated concept)
                    self.C_Id_derived_from_D_Id_entered = D_Id_data["concept_id"]
                    self.D_Id_active = D_Id_data["active_status"]
                    self.D_Term_derived_from_D_Id_entered = D_Id_data["term"]
                    self.D_Term_Type_derived_from_D_Id_entered = D_Id_data["term_type"]
                    self.C_Id = self.C_Id_derived_from_D_Id_entered
                    self.C_Id_source = "DERIVED"
                    self.C_Id_why_none = None
                    if self.D_Term_entered:
                        # self.congruence_of_D_Id_entered_and_D_Term_entered_case_insens=(D_Id_data["term"].lower()==self.D_Term_entered.lower())
                        self.congruence_of_D_Id_entered_and_D_Term_entered_case_insens = compare_strings_csr(
                            string1=D_Id_data["term"],
                            string2=self.D_Term_entered,
                            csr_indicator="ci",
                        )
                        self.congruence_of_D_Id_entered_and_D_Term_entered_csr = (
                            compare_strings_csr(
                                string1=D_Id_data["term"],
                                string2=self.D_Term_entered,
                                csr_SCT_code=D_Id_data["case_sig"],
                            )
                        )
                else:
                    if (
                        setchks_session.sct_version
                        == setchks_session.available_sct_versions[0]
                    ):  # if selected release is latest release
                        self.C_Id_why_none = "DID_NISR_SRIL"
                    else:  # look in latest release
                        D_Id_data_latest = ds.get_data_about_description_id(
                            description_id=self.D_Id_entered,
                            sct_version=setchks_session.available_sct_versions[0],
                        )
                        if D_Id_data_latest is not None:
                            self.C_Id_derived_from_D_Id_entered = D_Id_data_latest[
                                "concept_id"
                            ]
                            self.D_Id_active = D_Id_data_latest["active_status"]
                            self.D_Term_derived_from_D_Id_entered = D_Id_data_latest[
                                "term"
                            ]
                            self.D_Term_Type_derived_from_D_Id_entered = (
                                D_Id_data_latest["term_type"]
                            )
                            self.C_Id_via_latest_release = (
                                self.C_Id_derived_from_D_Id_entered
                            )
                            C_Id_data = ds.get_data_about_concept_id(
                                concept_id=self.C_Id_derived_from_D_Id_entered,
                                sct_version=setchks_session.sct_version,
                            )
                            if C_Id_data != []:
                                self.C_Id_why_none = "DID_NISR_DID_ILR_CID_ISR"
                            else:
                                self.C_Id_why_none = "DID_NISR_DID_ILR_CID_NISR"
                        else:
                            self.C_Id_why_none = "DID_NISR_DID_NILR"

            if self.C_Id_entered and self.D_Term_entered:
                C_Id_data = ds.get_data_about_concept_id(
                    concept_id=self.C_Id_entered,
                    sct_version=setchks_session.sct_version,
                )
                self.congruence_of_C_Id_entered_and_D_Term_entered_case_insens = False

                # remove inactive descriptions where there is an active description with precisely same Term
                # this is required because otherwise (in these odd cases) the loop-break construct below
                # may encounter the inactive term first and stop on that one without "realising" there is still an active
                # term to come in the loop
                active_terms = [
                    x["term"] for x in C_Id_data if x["active_status"] == "1"
                ]
                C_Id_data = [
                    x
                    for x in C_Id_data
                    if (
                        (x["active_status"] == "1")
                        or (
                            (x["active_status"] == "0")
                            and (x["term"] not in active_terms)
                        )
                    )
                ]

                # setup list to loop over items twice - once csr and once ci - see bug SIV-747
                # this method means that in the COW given and available descriptions - Cow and cow - then
                # just the first of these description encountered will be selected (outstanding "bug" SIV-752)
                items_list_csr = [(item, item["case_sig"]) for item in C_Id_data]
                items_list_ci = [(item, "ci") for item in C_Id_data]
                two_pass_items_list = items_list_csr + items_list_ci
                for item, csr_indicator in two_pass_items_list:
                    if compare_strings_csr(
                        string1=item["term"],
                        string2=self.D_Term_entered,
                        csr_indicator=csr_indicator,
                    ):  # look for first match, going over in csr fashion first and then ci until get a match
                        self.congruence_of_C_Id_entered_and_D_Term_entered_case_insens = (
                            True
                        )
                        self.D_Id_derived_from_C_Id_entered_and_D_Term_entered = item[
                            "desc_id"
                        ]
                        self.D_Id_active = item["active_status"]
                        self.D_Term_Type_derived_from_C_Id_entered_and_D_Term_entered = item[
                            "term_type"
                        ]
                        if item["case_sig"] == "ci" or compare_strings_csr(
                            string1=item["term"],
                            string2=self.D_Term_entered,
                            csr_SCT_code=item["case_sig"],
                        ):
                            self.congruence_of_C_Id_entered_and_D_Term_entered_csr = (
                                True
                            )
                        else:
                            self.D_Term_csr_correct_derived_from_C_Id_entered_and_D_Term_entered = item[
                                "term"
                            ]
                            self.congruence_of_C_Id_entered_and_D_Term_entered_csr = (
                                False
                            )
                        break

        # test for Excel corruption
        if self.C_Id is None and self.C_Id_why_none != "BLANK_ENTRY":
            flag, RC, RD, RC_in_release, RD_in_release = (
                detect_corruption_and_restore_id(
                    sctid=self.sctid_cell.string,
                    ds=ds,
                    sct_version=setchks_session.sct_version.date_string,
                )
            )
            self.excel_corruption_suspected = flag
            if self.excel_corruption_suspected and RC_in_release:
                self.possible_reconstructed_C_Id = RC
            if self.excel_corruption_suspected and RD_in_release:
                self.possible_reconstructed_D_Id = RD

    def __str__(self):
        output_str = "\n"
        for attribute in self.__slots__:
            output_str += "%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return output_str
