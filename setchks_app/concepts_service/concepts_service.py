"""Definition of class to interface to concepts_service database"""

import os
import requests
import shutil
import glob
import json

import logging

logger = logging.getLogger()

from pymongo import MongoClient

from setchks_app.sct_versions import get_sct_versions
from . import pull_concepts_from_ontoserver
from setchks_app.mongodb import get_mongodb_client
from setchks_app.descriptions_service.descriptions_service import DescriptionsService


class ConceptsService:

    __slots__ = ["_db"]

    def __init__(self):
        self._db = None
        # self.db=MongoClient()["concepts_service"]
        # self.db=MongoClient()["VSMT_uprot_app"]

    def get_list_of_releases_on_ontoserver(self):
        return [
            x.date_string for x in get_sct_versions.get_sct_versions_on_ontoserver()
        ]

    def check_have_sct_version_collection_in_db(self, sct_version=None):
        collection_name = self.make_collection_name(date_string=sct_version)
        return collection_name in self.db.list_collection_names()

    def delete_one_collection(self, sct_version=None):
        collection_name = self.make_collection_name(date_string=sct_version)
        self.db.drop_collection(collection_name)

    def get_collection_names(self):
        return sorted(list(self.db.list_collection_names()), reverse=True)

    def get_collection_size(self, sct_version=None):
        collection_name = self.make_collection_name(date_string=sct_version)
        return self.db[collection_name].count_documents({})

    def delete_database(self):
        get_mongodb_client.get_mongodb_client().drop_database("concepts_service")

    def make_missing_collections(self):
        hst = DescriptionsService(data_type="hst")

        existence_data = self.check_whether_releases_on_ontoserver_have_collections()
        for date_string, existence in existence_data.items():
            in_hst = hst.check_have_sct_version_collection_in_db(
                sct_version=date_string
            )
            if in_hst:
                if not existence:
                    print(
                        f"==============\nMaking collection for {date_string}\n=============="
                    )
                    self.create_collection_from_ontoserver(sct_version=date_string)
                else:
                    print(
                        "==============\nCollection already exists for %s\n=============="
                        % date_string
                    )
            else:
                print(
                    f"===============\nCollection not in hst for {date_string} so no need to get\n=============="
                )

    def check_whether_releases_on_ontoserver_have_collections(self):
        return_data = {}
        for sct_version in self.get_list_of_releases_on_ontoserver():
            # print("%s : %s" % (sct_version, self.check_have_sct_version_collection_in_db(sct_version=sct_version)))
            return_data[sct_version] = self.check_have_sct_version_collection_in_db(
                sct_version=sct_version
            )
        return return_data

    # def get_data_about_description_id(self, description_id=None, sct_version=None):
    #     """ returns the information associated with a particular description id in a particular release"""
    #     collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
    #     data_found=list(self.db[collection_name].find({"desc_id":str(description_id)}))
    #     if data_found==[]:
    #         return None
    #     else:
    #         assert(len(data_found)==1)
    #         return data_found[0]

    # def get_data_about_concept_id(self, concept_id=None, sct_version=None):
    #     """ returns the information associated with a particular concept id in a particular release"""
    #     collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
    #     data_found=list(self.db[collection_name].find({"concept_id":str(concept_id)}))
    #     return data_found

    def make_collection_name(self, date_string=None):
        return "concepts_" + date_string

    def create_collection_from_ontoserver(
        self, sct_version=None, delete_if_exists=False
    ):
        sct_version = sct_version

        # NEED TO IMPLEMENT DELETE IF EXISTS

        root_id = 138875005
        # root_id=280115004

        concepts = (
            pull_concepts_from_ontoserver.download_limited_concept_data_from_ontoserver(
                sct_version=sct_version,
                root_id=root_id,
            )
        )

        pull_concepts_from_ontoserver.transitive_closure(root_id, concepts, {})

        for code, concept in concepts.items():
            concept["ancestors"] = list(concept["ancestors"])
            concept["descendants"] = list(concept["descendants"])

        db_collection = self.db["concepts_" + sct_version]

        n_documents_per_chunk = 100000
        i_document = 0
        documents = []
        for code, concept in concepts.items():
            i_document += 1
            documents.append(concept)
            if i_document % n_documents_per_chunk == 0:
                logger.debug("Have sent %s documents to mongodb" % i_document)
                db_collection.insert_many(documents)
                documents = []
        db_collection.insert_many(documents)  # insert any left in the last set
        logger.debug("Finished sending %s documents to mongodb" % i_document)
        logger.debug("Creating indexes..")
        db_collection.create_index("code", unique=False)
        logger.debug(".. finished creating indexes..")

        # for code, concept in concepts.items():
        #     populate_collection.add_concept_to_db(concept=concept, db_document=db_document)

    @property
    def db(self):  # only connect the first time it is needed and then store it
        if self._db is None:
            self._db = get_mongodb_client.get_mongodb_client()["concepts_service"]
        return self._db
