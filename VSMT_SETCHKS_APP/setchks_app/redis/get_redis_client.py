
import os
import json

import logging
logger=logging.getLogger()

from flask import current_app

import redis
import boto3

def get_elasticache_endpoint():
    client=boto3.client('elasticache')
    response=client.describe_replication_groups(ReplicationGroupId='vsmt-redis-replication-group')
    logger.debug(f"response={response}")
    endpoint=response['ReplicationGroups'][0]['NodeGroups'][0]['PrimaryEndpoint']['Address']
    return endpoint

def get_redis_string():
    if os.environ["DEPLOYMENT_ENV"]=="AWS":
        logger.debug("Configuring redis to connect to elsticache")
        endpoint=get_elasticache_endpoint()
        redis_string=f'rediss://{endpoint}:6379'
        logger.debug(f'redis_string={redis_string}')
    else:
        logger.debug("Configuring redis to connect to localhost")
        redis_string='redis://localhost:6379'
    return redis_string

def get_redis_client():
    return redis.from_url(get_redis_string())