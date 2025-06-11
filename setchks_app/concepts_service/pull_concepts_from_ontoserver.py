#!/usr/bin/env python

import sys, os, pprint

from setchks_app.terminology_server_module import TerminologyServer

from fhir.resources.valueset import ValueSet


def transitive_closure(
    start_id, concepts, visited
):  # at first call pass in visited as empty dictionary

    # This is a straightforward translation of the perl script provided by IHTSDO
    # global counter
    # counter+=1
    # if counter%1000==0:
    #     print("Visit", start_id,counter)

    for child_id in concepts[start_id][
        "child"
    ]:  # for all the children of the startnode
        if child_id not in visited:  # if it has not already been traversed
            transitive_closure(
                child_id, concepts, visited
            )  # recursively visit the childnode
            visited[child_id] = (
                True  # and when the recursive visit completes, mark as visited
            )
        for descendant_id in concepts[child_id][
            "descendants"
        ]:  # for each descendant of childnode
            concepts[start_id]["descendants"].add(
                descendant_id
            )  # mark as a descendant of startnode
            concepts[descendant_id]["ancestors"].add(
                start_id
            )  # and ditto m.m. for ancestor
        concepts[start_id]["descendants"].add(
            child_id
        )  # mark the immediate childnode as a descendant of startnode
        concepts[child_id]["ancestors"].add(start_id)  # and ditto m.m. for ancestor


def download_limited_concept_data_from_ontoserver(sct_version=None, root_id=None):

    concepts = {}
    sct_version = "http://snomed.info/sct/83821000000107/version/" + sct_version
    # relative_sub_url= "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child" % (sct_version, "<<"+str(root_id))
    relative_sub_url = (
        "ValueSet/$expand?property=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child"
        % (sct_version, "*")
    )
    # relative_sub_url= "ValueSet/$expand?property=*&url=%s?fhir_vs=ecl/(%s)" % (sct_version, "*")
    # worked:   relative_sub_url= "ValueSet/$expand?url=%s?fhir_vs=ecl/(%s)" % (sct_version, "*")
    # relative_sub_url= "ValueSet/$expand?activeOnly=false&=inactive&url=%s?fhir_vs=ecl/(%s)&property=*&property=child" % (sct_version, "<<"+str(root_id))
    terminology_server = TerminologyServer()

    # work out how many fetches to do
    relative_url = relative_sub_url + "&count=0"
    response = terminology_server.do_get(relative_url=relative_url, verbose=True)
    temp_valueset = ValueSet.parse_obj(response.json())
    total_concepts = temp_valueset.expansion.total
    n_per_fetch = 1000
    n_fetches = int(total_concepts / n_per_fetch)
    if (total_concepts % n_per_fetch) != 0:
        n_fetches += 1
    print("Will fetch %s concepts in %s fetches" % (total_concepts, n_fetches))

    offset = 0
    while offset < total_concepts:
        print("offset = %s" % (offset))
        relative_url = relative_sub_url + "&count=%s&offset=%s" % (n_per_fetch, offset)
        terminology_server = (
            TerminologyServer()
        )  # call every time as bodge to prevent token expiring
        response = terminology_server.do_get(relative_url=relative_url, verbose=True)
        # print(response)
        # print(response.text)
        print("Parsing..")
        temp_valueset = ValueSet.parse_obj(response.json())
        # print("\n".join(vsmt_uprot.fhir_utils.repr_resource(temp_valueset)))

        for contained_item in temp_valueset.expansion.contains:
            concept = {}
            concept["parent"] = []
            concept["child"] = []
            concept["descendants"] = set()
            concept["ancestors"] = set()
            concept["display"] = contained_item.display
            concept["code"] = int(contained_item.code)
            # print(concept['code'])
            for item in contained_item.extension:
                if (
                    item.url
                    == "http://hl7.org/fhir/5.0/StructureDefinition/extension-ValueSet.expansion.contains.property"
                ):
                    property_value = None
                    for iv, value in enumerate(
                        [
                            item.extension[1].valueBoolean,
                            item.extension[1].valueString,
                            item.extension[1].valueCode,
                        ]
                    ):
                        if value is not None:
                            property_value = value
                    property_name = item.extension[0].valueCode
                    if property_name not in ["normalForm", "normalFormTerse"]:
                        if property_name in ["parent", "child"]:
                            concept[property_name].append(int(property_value))
                        else:
                            concept[property_name] = property_value
            concepts[concept["code"]] = concept
        offset += n_per_fetch
    return concepts


# def add_concept_to_db(concept=None, db_document=None):
#     print("Adding %s to db" % concept['code'])
#     db_document.insert_one(concept)
