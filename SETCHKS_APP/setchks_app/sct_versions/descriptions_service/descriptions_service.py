"""Definition of interface class to database of concept_id, description_id, decription_term tuples"""

class DescriptionsService():
    def __init__(self, mongodb_conn=None):
        self.mongodb_conn=mongodb_conn
    
    def get_collections(self):
        """ returns a list of the releases for which collections exist"""
        pass

    def create_collection_from_RF2_file(self, RF2_filename=None):
        """ creates a collection from a specified RF2 file"""
        pass

    def search_by_description_id(self, description_id=None, sct_version=None):
        """ returns the information associated with a particular description id in a particular release"""
        pass

    