"""Definition of interface class to database of concept_id, description_id, decription_term tuples"""

from . import RF2_handling
from pymongo import MongoClient

class DescriptionsService():
    def __init__(self):
        self.db=MongoClient()["descriptions_service"]
    
    def get_collections(self):
        """ returns a list of the releases for which collections exist"""
        pass

    def create_collection_from_RF2_file(self, RF2_filename=None, delete_if_exists=False):
            """ creates a collection from a specified RF2 file"""
            success_flag, message=RF2_handling.create_collection_from_RF2_file(db=self.db, RF2_filename=RF2_filename, delete_if_exists=delete_if_exists)
            return success_flag, message
        
    def search_by_description_id(self, description_id=None, sct_version=None):
        """ returns the information associated with a particular description id in a particular release"""
        pass

