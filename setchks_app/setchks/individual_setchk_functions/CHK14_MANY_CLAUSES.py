import os, copy, sys

import logging

logger = logging.getLogger()


import setchks_app.terminology_server_module

from setchks_app.set_refactoring import refactor_core_code
from setchks_app.set_refactoring.concept_module import ConceptsDict
from setchks_app.set_refactoring.valset_module import ClauseMembershipAnalysis

from ..set_level_table_row import SetLevelTableRow
from ..chk_specific_sheet import ChkSpecificSheet


def do_check(setchks_session=None, setchk_results=None):
    """
    This check is written on the assumption that it will not be run unless the gatekeeper controller gives the go ahead

    This check is written on the assumption that it can be called for all data_entry_extract_types
    """

    logging.info("Set Check %s called" % setchk_results.setchk_code)

    concepts = ConceptsDict(sct_version=setchks_session.sct_version.date_string)

    ##################################################################
    ##################################################################
    ##################################################################
    # Refactor value set                                             #
    ##################################################################
    ##################################################################
    ##################################################################

    value_set_members = set()

    for mr in setchks_session.marshalled_rows:
        concept_id = mr.C_Id
        if concept_id is not None:
            value_set_members.add(concept_id)

    # disable caching of refactored form as would have to be done differently since if running a batch of setchks in redis queue then
    # updates to setchks_session will be lost. Would have to run things like refactoring in a "pre" job
    # if setchks_session.refactored_form is None: # do refactoring if not already done
    original_valset, refactored_valset = refactor_core_code.refactor_core_code(
        valset_extens_defn=value_set_members,
        concepts=concepts,
    )
    # setchks_session.refactored_form=refactored_valset

    # setchk_results.set_analysis["Messages"]=[]
    # msg=(
    #     f"Refactored form:"
    #     )
    # setchk_results.set_analysis["Messages"].append(msg)

    n_INCLUDE_CLAUSES = 0
    n_EXCLUDE_CLAUSES = 0

    chk_specific_sheet = ChkSpecificSheet(sheet_name="Refactored")
    setchk_results.chk_specific_sheet = chk_specific_sheet
    chk_specific_sheet.col_widths = [15, 15, 15, 15, 120]

    row = chk_specific_sheet.new_row()
    row.cell_contents = [
        "Include / Exclude",
        "Number of Concepts in Clause",
        "Number of Concepts from Clause in Value Set",
        "Number of Concepts Excluded by Clause from Value Set",
        "Expression Constraint Language (ECL)",
    ]
    row = chk_specific_sheet.new_row()
    row.cell_contents = [
        "",
        "",
    ]
    ECL_clauses = {}
    ECL_clauses["include"] = []
    ECL_clauses["exclude"] = []

    ###########################
    # analyse include clauses #
    ###########################
    all_included_concepts = set()
    includes_staging_list = []
    for clause in refactored_valset.clause_based_rule.clauses:
        if clause.clause_type == "include":
            n_INCLUDE_CLAUSES += 1
            clause_members = set(
                ClauseMembershipAnalysis(
                    clause=clause,
                    concepts=concepts,
                ).members
            )
            clause_members = set(str(x) for x in clause_members)
            all_included_concepts.update(clause_members)
            n_clause_members = len(clause_members)
            n_clause_members_in_value_set = len(
                clause_members.intersection(value_set_members)
            )
            includes_staging_list.append(
                (clause, n_clause_members, n_clause_members_in_value_set)
            )
    includes_staging_list.sort(key=lambda x: x[1], reverse=True)

    ###########################
    # analyse exclude clauses #
    ###########################
    excludes_staging_list = []
    for clause in refactored_valset.clause_based_rule.clauses:
        if clause.clause_type == "exclude":
            n_EXCLUDE_CLAUSES += 1
            clause_members = set(
                ClauseMembershipAnalysis(
                    clause=clause,
                    concepts=concepts,
                ).members
            )
            clause_members = set(str(x) for x in clause_members)
            n_clause_members = len(clause_members)
            n_clause_members_excluded_from_value_set = len(
                clause_members.intersection(all_included_concepts)
            )
            excludes_staging_list.append(
                (clause, n_clause_members, n_clause_members_excluded_from_value_set)
            )
    excludes_staging_list.sort(key=lambda x: x[1], reverse=True)

    for staging_list in [includes_staging_list, excludes_staging_list]:
        for clause, n_clause_members, nnn in staging_list:
            clause_base_concept_id = str(clause.clause_base_concept_id)
            clause_type = clause.clause_type
            clause_operator = clause.clause_operator
            if clause_operator[0] == "=":
                clause_operator = clause_operator[1:]
            pt = concepts[clause_base_concept_id].pt
            ECL_clause = (
                f"{clause_operator:2} {clause_base_concept_id} | {pt} |".strip()
            )
            ECL_clauses[clause_type].append(ECL_clause)
            if (
                clause_type == "include"
            ):  # work what nnn represents and allocate to correct column of output
                n1 = nnn
                n2 = ""
            else:
                n1 = ""
                n2 = nnn
            row = chk_specific_sheet.new_row()
            row.cell_contents = [
                clause_type,
                n_clause_members,
                n1,
                n2,
                ECL_clause,
            ]
        row = chk_specific_sheet.new_row()  # blank row

    ##########################################
    # Make full ECL expression for value set #
    ##########################################
    include_ECL = "(" + " OR ".join(ECL_clauses["include"]) + ")"
    exclude_ECL = "(" + " OR ".join(ECL_clauses["exclude"]) + ")"
    full_ECL = include_ECL
    if ECL_clauses["exclude"] != []:
        full_ECL += " MINUS " + exclude_ECL
    row = chk_specific_sheet.new_row()
    row.cell_contents = [
        "Full ECL expression:",
        "",
        "",
        "",
        full_ECL,
    ]

    n_CLAUSES = n_INCLUDE_CLAUSES + n_EXCLUDE_CLAUSES
    if n_CLAUSES > 30:
        # <set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=(
                    "[AMBER] There are more than 30 clauses in the refactored form. "
                    "This suggests that either you have a very scattered set of clauses, or "
                    "that you are trying to cover too large a scope with one value set."
                ),
                outcome_code="CHK14-OUT-01",
            )
        )
        # </set_level_message>
        # <set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=("Total number of clauses in the refactored form"),
                value=f"{n_CLAUSES}",
                outcome_code="CHK14-OUT-02",
            )
        )
        # </set_level_count>

        # <set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=("Number of include clauses in the refactored form"),
                value=f"{n_INCLUDE_CLAUSES}",
                outcome_code="CHK14-OUT-03",
            )
        )
        # </set_level_count>

        # <set_level_count>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                descriptor=("Number of exclude clauses in the refactored form"),
                value=f"{n_EXCLUDE_CLAUSES}",
                outcome_code="CHK14-OUT-04",
            )
        )
        # </set_level_count>
    else:
        # <set_level_message>
        setchk_results.set_level_table_rows.append(
            SetLevelTableRow(
                simple_message=("[GREEN] This check has detected no issues."),
                outcome_code="CHK14-OUT-06",
            )
        )
        # </set_level_message>
