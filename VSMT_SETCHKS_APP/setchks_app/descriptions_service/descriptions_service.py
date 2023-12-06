"""Definition of interface class to database of concept_id, description_id, decription_term tuples"""

import os
import requests
import shutil
import glob
import json

import logging
logger=logging.getLogger

from flask import current_app

from . import RF2_handling
from setchks_app.mongodb import get_mongodb_client

# from pymongo import MongoClient

from setchks_app.sct_versions import get_sct_versions

class DescriptionsService():

    __slots__=[
        "_db",
        "data_type",
        ]

    def __init__(self, data_type="descriptions"):
        self._db=None
        self.data_type=data_type

    def create_collection_from_RF2_file(
        self, 
        RF2_filename=None, 
        RF2_filename2=None, 
        delete_if_exists=False, 
        collection_name=None
        ):
        """ creates a collection from a specified RF2 file"""
        success_flag, message=RF2_handling.create_collection_from_RF2_file(
            db=self.db, 
            RF2_filename=RF2_filename,
            RF2_filename2=RF2_filename2, 
            delete_if_exists=delete_if_exists,
            data_type=self.data_type,
            collection_name=collection_name,
            )
        return success_flag, message
    
    def delete_one_collection(self, sct_version=None):
        collection_name=self.make_collection_name(date_string=sct_version)
        self.db.drop_collection(collection_name)

    def get_collection_names(self):
        return sorted(list(self.db.list_collection_names()), reverse=True)
    
    def get_collection_size(self, sct_version=None):
        collection_name=self.make_collection_name(date_string=sct_version)
        return self.db[collection_name].count_documents({})
    
    def get_list_of_releases_on_ontoserver(self):
        return [x.date_string for x in get_sct_versions.get_sct_versions()]
    
    def make_collection_name(self, date_string=None):
        if self.data_type=="descriptions":
            return f"sct2_Description_MONOSnapshot-en_GB_{date_string}"
        elif self.data_type=="hst":
            # return f"xres2_HistorySubstitutionTable_Concepts_GB1000000_{date_string}"
            # return f"HistorySubstitutionTable_Concepts_GB1000000_{date_string}" # slightly shorter than actual trud filename
            #                                                                     # to avoid 57 char limit on DocumentDB collection names
            return f"hst_{date_string}" # drastically slightly shorter than actual trud filename
                                                            # to avoid 57 char limit on DocumentDB collection names
                                                            # and 63 char limit on index names as col.$<index>
        elif self.data_type=="qt":
            return f"xres2_SNOMEDQueryTable_CORE-UK_{date_string}"
        else:
            return None
    def check_have_sct_version_collection_in_db(self, sct_version=None):
        # collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version
        collection_name=self.make_collection_name(date_string=sct_version)
        return collection_name in self.db.list_collection_names()
    
    def delete_database(self):
        if self.data_type=="descriptions":
            get_mongodb_client.get_mongodb_client().drop_database("descriptions_service")
        elif self.data_type=="hst":
            get_mongodb_client.get_mongodb_client().drop_database("hst")
        elif self.data_type=="qt":
            get_mongodb_client.get_mongodb_client().drop_database("qt")

    
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
        if self.data_type=="descriptions":
            url="https://isd.digital.nhs.uk/trud/api/v1/keys/%s/items/1799/releases" % (
                os.environ["TRUDAPIKEY"],
            )
        elif self.data_type in ["hst", "qt"]:
            url="https://isd.digital.nhs.uk/trud/api/v1/keys/%s/items/276/releases" % (
                os.environ["TRUDAPIKEY"],
            )
        else:
            return None

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

        # if self.db is None: # for running this via redis queue cannot send the mongodb_connection through so have to make afresh
        #     print("Making new mongo db connection")
        #     self.db=get_mongodb_client.get_mongodb_client()["descriptions_service"]

        trud_dict=self.get_trud_releases_info()

        if date_string not in trud_dict:
            logging.debug(f"{date_string} does not have a trud release for {self.data_type}")
            return 

        filename, url= trud_dict[date_string]
        
        # url above will be of form resulting from this:
        # url="https://isd.digital.nhs.uk/download/api/v1/keys/%s/content/items/1799/uk_sct2mo_36.5.0_20230830000001Z.zip" % (
        #     os.environ["TRUDAPIKEY"],
        # )
        
        print("fetching file from", url)
        response = requests.get(url)
        download_folder="/tmp/trud_download_temp_files"
        os.system(f"mkdir {download_folder}") # in case does not already exist
        out_file=f'{download_folder}/{filename}'
        
        print("writing file to", out_file)
        ofh=open(out_file,'wb')
        ofh.write(response.content)
        
        extract_dir=out_file[:-4]
        os.makedirs(extract_dir, exist_ok=True)
        print("extracting file to", extract_dir)
        shutil.unpack_archive(out_file, extract_dir)

        print("Making collection..")
        if self.data_type=="descriptions":
            glob_pattern=extract_dir+"/*/Snapshot/Terminology/sct2_Description_*"
            glob_pattern2=extract_dir+"/*/Snapshot/Refset/Language/der2_cRefset_Language*"
        elif self.data_type=="hst":
            glob_pattern=extract_dir+"/*/Resources/HistorySubstitutionTable/xres*"
            glob_pattern2=None
        elif self.data_type=="qt":
            glob_pattern=extract_dir+"/*/Resources/QueryTable/xres*"
            glob_pattern2=None
        else:
            glob_pattern=None             

        data_filename=glob.glob(glob_pattern)[0]
        if glob_pattern2 is not None:
            data_filename2=glob.glob(glob_pattern2)[0]
        else:
            data_filename2=None
        success_flag, message= self.create_collection_from_RF2_file(
            RF2_filename=data_filename,
            RF2_filename2=data_filename2,
            delete_if_exists=True,
            collection_name=self.make_collection_name(date_string),
            )
    
        print("Cleaning up")

        shutil.rmtree(extract_dir)
        os.remove(out_file)
 
        logging.debug("%s : %s" % (success_flag,message))

    def get_data_about_description_id(self, description_id=None, date_string=None, sct_version=None):
        """ returns the information associated with a particular description id in a particular release"""
        # collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
        if date_string is None:
            date_string=sct_version.date_string
        
        collection_name=self.make_collection_name(date_string=date_string)

        data_found=list(self.db[collection_name].find({"desc_id":str(description_id)}))
        if data_found==[]:
            return None
        else:
            assert(len(data_found)==1)
            return data_found[0]
        
    def get_data_about_concept_id(self, concept_id=None, date_string=None, sct_version=None):
        """ returns the information associated with a particular concept id in a particular release"""
        # collection_name="sct2_Description_MONOSnapshot-en_GB_%s" % sct_version.date_string
        if date_string is None:
            date_string=sct_version.date_string
        collection_name=self.make_collection_name(date_string=date_string)
        data_found=list(self.db[collection_name].find({"concept_id":str(concept_id)}))
        return data_found
    
    def get_hst_data_from_old_concept_id(self, old_concept_id=None, sct_version=None):
        """ returns the hst information associated with a particular concept id as old_concept_id in a particular release"""
        collection_name=self.make_collection_name(date_string=sct_version.date_string)
        data_found=list(self.db[collection_name].find({"old_concept_id":str(old_concept_id)}))
        return data_found
    
    def get_hst_data_from_new_concept_id(self, new_concept_id=None, sct_version=None):
        """ returns the hst information associated with a particular concept id as new_concept_id in a particular release"""
        collection_name=self.make_collection_name(date_string=sct_version.date_string)
        data_found=list(self.db[collection_name].find({"new_concept_id":str(new_concept_id)}))
        return data_found
    
    @property
    def db(self): # only connect the first time it is needed and then store it
        if self._db is None:
            if self.data_type=="descriptions":
                self._db=get_mongodb_client.get_mongodb_client()["descriptions_service"]
            elif self.data_type=="hst":
                self._db=get_mongodb_client.get_mongodb_client()["hst"]
            elif self.data_type=="qt":
                self._db=get_mongodb_client.get_mongodb_client()["qt"]
            else:
                self.db=None
        return self._db 


    