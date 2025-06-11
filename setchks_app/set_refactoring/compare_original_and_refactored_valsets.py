from setchks_app.set_refactoring import valset_module


def compare_original_and_refactored_valsets(
    valsets=None,
    concepts=None,
    input_valset_name="input",
    output_valset_name="output",
    elapsed_time=-999,
):
    original_valset = valsets[valsets.valset_name_to_id[input_valset_name]]
    refactored_valset = valsets[valsets.valset_name_to_id[output_valset_name]]

    refactored_membership_analysis = valset_module.ValsetMembershipAnalysis(
        valset=refactored_valset, concepts=concepts
    )
    original_membership_analysis = valset_module.ValsetMembershipAnalysis(
        valset=original_valset,
        concepts=concepts,
        global_exclusions=valsets.global_exclusions,
        stub_out_interaction_matrix_calc=True,
        verbose=True,
    )

    original_members = set(original_membership_analysis.final_inclusion_list)
    refactored_members = set(refactored_membership_analysis.final_inclusion_list)

    if original_members == refactored_members:
        concepts_identical = "CONCEPTS_True"
    else:
        concepts_identical = "CONCEPTS_False"

    print("\nOriginal valset has %s members" % len(original_members))
    print("Refactored valset has %s members" % len(refactored_members))
    print(
        "\nConcepts in original and not in refactored valset: %s"
        % original_members.difference(refactored_members)
    )
    print(
        "Concepts in refactored and not in original valset: %s"
        % refactored_members.difference(original_members)
    )

    original_include_clause_strings = {
        clause.clause_string
        for clause in original_valset.clause_based_rule.clauses
        if clause.clause_type == "include"
    }
    original_exclude_clause_strings = {
        clause.clause_string
        for clause in original_valset.clause_based_rule.clauses
        if clause.clause_type == "exclude"
    }

    refactored_include_clause_strings = {
        clause.clause_string
        for clause in refactored_valset.clause_based_rule.clauses
        if clause.clause_type == "include"
    }
    refactored_exclude_clause_strings = {
        clause.clause_string
        for clause in refactored_valset.clause_based_rule.clauses
        if clause.clause_type == "exclude"
    }

    print(
        "Original:   %3d include clauses and %3d exclude clauses"
        % (len(original_include_clause_strings), len(original_exclude_clause_strings))
    )
    print(
        "Refactored: %3d include clauses and %3d exclude clauses"
        % (
            len(refactored_include_clause_strings),
            len(refactored_exclude_clause_strings),
        )
    )

    include_clauses_only_in_original = original_include_clause_strings.difference(
        refactored_include_clause_strings
    )
    include_clauses_only_in_refactored = refactored_include_clause_strings.difference(
        original_include_clause_strings
    )
    exclude_clauses_only_in_original = original_exclude_clause_strings.difference(
        refactored_exclude_clause_strings
    )
    exclude_clauses_only_in_refactored = refactored_exclude_clause_strings.difference(
        original_exclude_clause_strings
    )

    if (original_include_clause_strings == refactored_include_clause_strings) and (
        original_exclude_clause_strings == refactored_exclude_clause_strings
    ):
        clauses_identical = "CLAUSES_True"
    else:
        clauses_identical = "CLAUSES_False"

    print("")
    for set_name in [
        "include_clauses_only_in_original",
        "include_clauses_only_in_refactored",
        "exclude_clauses_only_in_original",
        "exclude_clauses_only_in_refactored",
    ]:
        set_contents = eval(set_name)
        # print(set_name, set_contents)
        if set_contents:
            # for base_concept_id in set_contents:
            for clause_string in set_contents:
                print(clause_string)
                # find the clause with this base_concept_id (bit clunky..)
                # clause_string=None
                base_concept_id = None
                if "original" in set_name:
                    r = original_valset
                else:
                    r = refactored_valset
                for clause in r.clause_based_rule.clauses:
                    # if clause.clause_base_concept_id==base_concept_id:
                    #     clause_string=clause.clause_string
                    if clause.clause_string == clause_string:
                        base_concept_id = clause.clause_base_concept_id
                        if concepts[base_concept_id] is not None:
                            pt = concepts[base_concept_id].pt
                        else:
                            pt = "PROBABLY INACTIVE CONTENT: SUCH CONCEPTS TBI"
                print("%34s: %20s %s " % (set_name, clause_string, pt))
        else:
            print("%34s: None" % (set_name))
        print("")

    print(
        "\n\nREFACTOR_SUMMARY: %15s %15s | %5d %5d | %3d %3d | %3d %3d | %3d %3d | %3d %3d | %5.1f | %20s | %s \n\n"
        % (
            concepts_identical,
            clauses_identical,
            len(original_members),
            len(refactored_members),
            len(original_include_clause_strings),
            len(original_exclude_clause_strings),
            len(refactored_include_clause_strings),
            len(refactored_exclude_clause_strings),
            len(include_clauses_only_in_original),
            len(include_clauses_only_in_refactored),
            len(exclude_clauses_only_in_original),
            len(exclude_clauses_only_in_refactored),
            elapsed_time,
            original_valset.valset_name,
            original_valset.valset_description,
        )
    )
