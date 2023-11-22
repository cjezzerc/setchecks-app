""" creates a collection from a specified RF2 file"""

import logging
logger=logging.getLogger(__name__)

def create_collection_from_RF2_file(
        db=None, 
        RF2_filename=None, 
        RF2_filename2=None, 
        delete_if_exists=False,
        data_type=None,
        collection_name=None
        ):

    # f=RF2_filename.split("/")
    # collection_name=f[-1].split(".")[0]
    logger.debug("Creating collection" + str(collection_name))

    collection=db[collection_name]

    if collection.name in db.list_collection_names():
        if delete_if_exists==True:
            logger.debug("Deleting collection %s" % collection_name)
            db.drop_collection(collection.name)
        else:
            logger.debug("Collection %s already exists" % collection_name)
            return False, "Collection %s already exists; use delete_if_exists=True to overwrite" % collection_name


    # for descriptions, additionally read the language file and build dict of acc/pref keyed by D_Id
    if data_type=="descriptions":
        acceptabilities={}
        for line in open(RF2_filename2).readlines()[1:]: 
            line=line.strip()
            f=line.split('\t')
            acceptability_active_status=f[2]
            refsetId=f[4]
            referenceComponentId=f[5]
            acceptabilityId=f[6].strip()
            # import pdb; pdb.set_trace()
            if refsetId=="999001261000000100": # NHS realm lang refset (clinical part)
                assert referenceComponentId not in acceptabilities # double check no duplicates
                if acceptability_active_status=="1":
                    if acceptabilityId=="900000000000548007": # = preferred
                        acceptabilities[referenceComponentId]="pref"
                    else:
                        acceptabilities[referenceComponentId]="acceptable"
                else:
                    pass    # acceptabilities entry will be missing if the active status in the 
                            # lang refset is 0, which can be considered same as "is no longer in the refset"

    n_documents_per_chunk=100000
    i_document=0
    documents=[]
    for line in open(RF2_filename).readlines()[1:]:
        i_document+=1
        f=[x.strip() for x in line.split('\t')]
        if data_type=="descriptions":
            desc_id=f[0]
            active_status=f[2]
            concept_id=f[4]
            typeId=f[6]
            term=f[7]
            case_sig=f[8]

            if desc_id in acceptabilities: # (only add description if not "unnacceptable" i.e must be (active) in lang refset)
                acceptability=acceptabilities[desc_id]
                if typeId=="900000000000003001": # = fsn
                    if acceptability=="pref":
                        term_type="fsn" 
                    else: # ?? can an fsn have acceptable status?
                        print(f"fsn with only acceptable status {desc_id}")
                        term_type="ignore"
                else:
                    if acceptability=="pref":
                        term_type="pt"
                    else:
                        term_type="syn"
                # print(acceptability, desc_id, typeId, term_type)
                document={
                    "desc_id":desc_id,
                    "active_status":active_status,
                    "concept_id":concept_id,
                    "term":term,
                    "term_type":term_type,
                    "case_sig":case_sig
                    }
            else:
                term_type="ignore"
            if term_type!="ignore":
                documents.append(document)
        elif data_type=="qt":
            supertype_id=f[0]
            subtype_id=f[1]
            provenance=f[2]
            document={
                "supertype_id":supertype_id,
                "subtype_id":subtype_id,
                "provenance":provenance,
                }
            documents.append(document)
        elif data_type=="hst":
            old_concept_id=f[0]
            old_concept_status=f[1]
            new_concept_id=f[2]
            new_concept_status=f[3]
            path=f[4]
            is_ambiguous=f[5]
            iterations=f[6]
            document={
                "old_concept_id":old_concept_id,
                "old_concept_status":old_concept_status,
                "new_concept_id":new_concept_id,
                "new_concept_status":new_concept_status,
                "path":path,
                "is_ambiguous":is_ambiguous,
                "iterations":iterations,
                }
            documents.append(document)
        else:
            raise Exception(f"Unknown data_type: {data_type}") 
        if i_document%n_documents_per_chunk==0:
            logger.debug("Have sent %s documents to mongodb" % i_document)
            print(i_document)
            if documents != []: # need check as unacceptable descriptions are skipped
                collection.insert_many(documents)
            documents=[]
    if documents != []: # need check as unacceptable descriptions are skipped 
        collection.insert_many(documents) # insert any left in the last set
    logger.debug("Finished sending %s documents to mongodb" % i_document)
    logger.debug("Creating indexes..")
    if data_type=="descriptions":
        collection.create_index("concept_id", unique=False)
        collection.create_index("desc_id", unique=True)
        collection.create_index("term", unique=False)
    elif data_type=="qt":
        collection.create_index("supertype_id", unique=False)
        collection.create_index("subtype_id", unique=False)
    elif data_type=="hst":
        collection.create_index("old_concept_id", unique=False)
        collection.create_index("new_concept_id", unique=False)
    logger.debug(".. finished creating indexes..")

    return True, "Created collection %s OK" % collection_name
