"""Definition of interface class to database of concept_id, description_id, decription_term tuples"""

import os
import requests
import shutil
import glob

import logging
logger=logging.getLogger

from . import RF2_handling
from pymongo import MongoClient

from setchks_app.sct_versions import get_sct_versions

class DescriptionsService():
    def __init__(self):
        self.db=MongoClient()["descriptions_service"]
    
    def create_collection_from_RF2_file(self, RF2_filename=None, delete_if_exists=False):
        """ creates a collection from a specified RF2 file"""
        success_flag, message=RF2_handling.create_collection_from_RF2_file(db=self.db, RF2_filename=RF2_filename, delete_if_exists=delete_if_exists)
        return success_flag, message
    
    def get_list_of_releases_on_ontoserver(self):
        return [x.date_string for x in get_sct_versions.get_sct_versions()]
    
    def check_have_sct_version_collection_in_db(self, sct_version=None):
        collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version
        return collection_name in self.db.list_collection_names()
    
 
    def make_missing_collections(self):
        existence_data=self.check_whether_releases_on_ontoserver_have_collections()
        for date_string, existence in existence_data.items():
            if not existence:
                print("==============\nMaking collection for %s\n==============" % date_string)
                self.pull_release_from_trud(date_string=date_string)

            else:
                print("==============\nCollection already exists for %s\n==============" % date_string)

 
    def check_whether_releases_on_ontoserver_have_collections(self):
        return_data={}
        for sct_version in self.get_list_of_releases_on_ontoserver():
            # print("%s : %s" % (sct_version, self.check_have_sct_version_collection_in_db(sct_version=sct_version)))
            return_data[sct_version]=self.check_have_sct_version_collection_in_db(sct_version=sct_version)
        return return_data
    
    def get_trud_releases_info(self):
        url="https://isd.digital.nhs.uk/trud/api/v1/keys/%s/items/1799/releases" % (
            os.environ["TRUDAPIKEY"],
        )
        response = requests.get(url)
        data=response.json()
        trud_dict={}
        for release in data["releases"]:
            filename=release["archiveFileName"]
            url=release["archiveFileUrl"]
            date_string=filename.split("_")[3][:8]
            trud_dict[date_string]=[filename, url]
            # print("%s : %s" % (date_string, url))
        return trud_dict
    
    def pull_release_from_trud(self, date_string=None):
        trud_dict=self.get_trud_releases_info()
        filename, url= trud_dict[date_string]
        
        # url above will be of form resulting from this:
        # url="https://isd.digital.nhs.uk/download/api/v1/keys/%s/content/items/1799/uk_sct2mo_36.5.0_20230830000001Z.zip" % (
        #     os.environ["TRUDAPIKEY"],
        # )

        print("fetching file from", url)
        response = requests.get(url)
        out_file='/tmp/trud_download_temp_files/' + filename
        
        print("writing file to", out_file)
        ofh=open(out_file,'wb')
        ofh.write(response.content)
        
        extract_dir=out_file[:-4]
        os.makedirs(extract_dir, exist_ok=True)
        print("extracting file to", extract_dir)
        shutil.unpack_archive(out_file, extract_dir)

        print("Making collection..")
        glob_pattern=extract_dir+"/*/Snapshot/Terminology/sct2_Description_*"
        descriptions_file=glob.glob(glob_pattern)[0]
        success_flag, message= self.create_collection_from_RF2_file(
            RF2_filename=descriptions_file,
            delete_if_exists=True,
            )
    
        print("Cleaning up")
        shutil.rmtree(extract_dir)
        os.remove(out_file)

 
        logging.debug("%s : %s" % (success_flag,message))

    def search_by_description_id(self, description_id=None, sct_version=None):
        """ returns the information associated with a particular description id in a particular release"""
        collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version
        data_found=self.db[collection_name].find_one({"desc_id":str(description_id)})
        return data_found
        pass

    