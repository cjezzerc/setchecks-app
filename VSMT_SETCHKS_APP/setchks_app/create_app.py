import os

from flask import Flask
import flask_session
import boto3
import json

import logging
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
logger=logging.getLogger(__name__)

from setchks_app.redis.get_redis_client import get_redis_client

def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'BAD_SECRET_KEY'

    flask_session_type="redis" # "redis" or "mongodb"
    # flask_session_type="mongodb" # "redis" or "mongodb"

    if flask_session_type=="redis":
        import redis
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        redis_connection=get_redis_client()
        app.config['SESSION_REDIS'] = redis_connection
        

    # get CA file for DocumentDB (do this even if connecting to a local mongoDB for debugging of CA file download) 
    import requests
    logger.debug(f'About to grab global-bundle-pem')
    r=requests.get("https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem")
    filename="/tmp/global-bundle.pem"
    ofh=open(filename,'w')
    byes_written=ofh.write(r.text)
    logger.debug(f'Wrote {byes_written} bytes to {filename}')

    # get secrets if necessary (but why not test DEPLYOMENT_ENV?)
    logger.debug("About to see if need to get secrets")
    if 'ONTOSERVER_USERNAME' not in os.environ:
        logger.debug("getting secrets")
        # os.environ['ONTOSERVER_INSTANCE']='https://dev.ontology.nhs.uk/dev1/fhir/'
        # os.environ['ONTOAUTH_INSTANCE']='https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token'
        sm_client = boto3.client('secretsmanager', region_name='eu-west-2')
        pw_response = sm_client.get_secret_value(SecretId='vsmt-ontoserver-access')
        passwords = pw_response['SecretString']
        dictionary_pw = json.loads(passwords)
        os.environ['ONTOSERVER_USERNAME']=dictionary_pw['ONTOSERVER_USERNAME']
        os.environ['ONTOSERVER_SECRET']=dictionary_pw['ONTOSERVER_SECRET']
        os.environ['TRUDAPIKEY']=dictionary_pw['TRUDAPIKEY']
        os.environ['DOCUMENTDB_USERNAME']=dictionary_pw['DOCUMENTDB_USERNAME']
        os.environ['DOCUMENTDB_PASSWORD']=dictionary_pw['DOCUMENTDB_PASSWORD']
        logger.debug("got secrets")
    else:
        logger.debug("no need to get secrets")
    logger.debug("OS_ENVIRON_KEYS:"+str(list(os.environ.keys())))


    if flask_session_type=="mongodb":   # STILL NEED TO CHANGE THIS IF WANT  ATTACH TO DOCUMENTDB!!!
        # currently requires pymngo <v4 see:
        # https://stackoverflow.com/questions/72025723/how-to-configure-mongodb-for-flask-session
        from pymongo import MongoClient
        print(app.config.keys())
        app.config['SESSION_TYPE'] = 'mongodb'
        app.config['SESSION_PERMANENT'] = True  # this seems to get round bug:
                                                # TypeError: '<=' not supported between instances of 'NoneType' and 'datetime.datetime'

        app.config['SESSION_USE_SIGNER'] = True
        if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
            print("Configuring mongodb to connect to mongo-server docker")
            app.config['SESSION_MONGODB']=MongoClient('mongo-server',27017)
        else:
            print("Configuring mongodb to connect to localhost")
            app.config['SESSION_MONGODB']=MongoClient()


    server_session = flask_session.Session(app) # resets session variable behaviour so uses redis
    
    from . import setchks_app
    app.register_blueprint(setchks_app.bp)

    return app

