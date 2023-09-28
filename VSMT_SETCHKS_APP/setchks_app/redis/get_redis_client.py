
import os
import json

import logging
logger=logging.getLogger()

import redis
import boto3

def get_elasticache_endpoint():
    client=boto3.client('elasticache')
    response=client.describe_replication_groups(ReplicationGroupId='vsmt-redis-replication-group')
    logger.debug(f"response={response}")
    endpoint=response['ReplicationGroups'][0]['NodeGroups'][0]['PrimaryEndpoint']['Address']
    return endpoint

def get_redis_string():
    if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
        logger.debug("Configuring redis to connect to redis-server docker")
        redis_string='redis://redis-server:6379'
    elif os.environ["DEPLOYMENT_ENV"]=="AWS":
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