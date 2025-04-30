#################################
#################################
# Simple mongodb check endpoint #
#################################
#################################

import datetime, logging

from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only
from setchks_app.mongodb import get_mongodb_client

logger=logging.getLogger(__name__)

@auth_required
@admin_users_only
def mongodb_check():
    logger.info("mongodb check called")

    mongodb_client=get_mongodb_client.get_mongodb_client()
    collection=mongodb_client["mongodb_check"]["mongodb_check"]
    logger.info("mongodb connection to db made")
    collection.insert_one({"insert_time": datetime.datetime.now().strftime('%d_%b_%Y__%H_%M_%S')})
    logger.info("inserted document")
    output_strings=["Collection 'mongodb check' contents:"]
    for doc in collection.find():
        output_strings.append(str(doc))
    output_strings.append("/nDatabase contents:")
    for db_name in mongodb_client.list_database_names():
        db=mongodb_client[db_name]
        logger.debug("db_name")
        for c_name in db.list_collection_names():
            logger.debug("db_name"+"-"+c_name)
            c=db[c_name]
            output_strings.append(f'db: {db_name:30s} collection:{c_name:30s}')                

    return '<br>'.join(output_strings)
