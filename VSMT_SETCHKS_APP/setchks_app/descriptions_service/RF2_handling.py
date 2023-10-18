""" creates a collection from a specified RF2 file"""

import logging
logger=logging.getLogger(__name__)

def create_collection_from_RF2_file(db=None, RF2_filename=None, delete_if_exists=False):

    # RF2_filename="/cygdrive/c/Users/jeremy/BIG_DATA_temp/uk_sct2mo_36.3.0_20230705000001Z/SnomedCT_MonolithRF2_PRODUCTION_20230705T120000Z/Snapshot/Terminology/sct2_Description_MONOSnapshot-en_GB_20230705.txt"
    f=RF2_filename.split("/")
    collection_name=f[-1].split(".")[0]
    logger.debug("Creating collection" + str(collection_name))

    collection=db[collection_name]

    if collection.name in db.list_collection_names():
        if delete_if_exists==True:
            logger.debug("Deleting collection %s" % collection_name)
            db.drop_collection(collection.name)
        else:
            logger.debug("Collection %s already exists" % collection_name)
            return False, "Collection %s already exists; use delete_if_exists=True to overwrite" % collection_name

    n_documents_per_chunk=100000
    i_document=0
    documents=[]
    for line in open(RF2_filename).readlines()[1:]: 
        i_document+=1
        f=line.split('\t')
        desc_id=f[0]
        active_status=f[2]
        concept_id=f[4]
        term=f[7]
        case_sig=f[8]
        document={"desc_id":desc_id,
                "active_status":active_status,
                "concept_id":concept_id,
                "term":term,
                "case_sig":case_sig
                }
        documents.append(document)
        if i_document%n_documents_per_chunk==0:
            logger.debug("Have sent %s documents to mongodb" % i_document)
            print(i_document)
            collection.insert_many(documents)
            documents=[]
    collection.insert_many(documents) # insert any left in the last set
    logger.debug("Finished sending %s documents to mongodb" % i_document)
    logger.debug("Creating indexes..")
    collection.create_index("concept_id", unique=False)
    collection.create_index("desc_id", unique=True)
    collection.create_index("term", unique=False)
    logger.debug(".. finished creating indexes..")

    return True, "Created collection %s OK" % collection_name
