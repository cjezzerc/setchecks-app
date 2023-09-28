""" make mongodb connection according to whether LOCAL, AWS etc """

import os

import json
import boto3

import logging
logger=logging.getLogger()

from pymongo import MongoClient

def get_documentdb_endpoint():
    client=boto3.client('docdb')
    response=client.describe_db_clusters(DBClusterIdentifier='vsmt-docdb-cluster')
    logger.debug(f"response={response}")
    endpoint=response['DBClusters'][0]['Endpoint']
    return endpoint

def get_mongodb_client():
    logger.debug("Getting mongodb client..")
    if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
        logger.debug("Configuring mongodb to connect to mongo-server docker")
        mongodb_client=MongoClient('mongo-server',27017)
    elif os.environ["DEPLOYMENT_ENV"]=="AWS":
        logger.debug("Configuring mongodb to connect to DocumentDB")
        endpoint=get_documentdb_endpoint()
        url_root=f'mongodb://{os.environ["DOCUMENTDB_USERNAME"]}:{os.environ["DOCUMENTDB_PASSWORD"]}@{endpoint}:27017/'
        arguments='?tls=true&tlsCAFile=/tmp/global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
        connection_string=url_root+arguments
        logger.debug(f"Connection string to mongodb is {connection_string}")
        mongodb_client=MongoClient(connection_string)
    else:
        logger.debug("Configuring mongodb to connect to localhost")
        mongodb_client=MongoClient()   
    return mongodb_client