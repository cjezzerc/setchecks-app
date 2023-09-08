import os

from flask import Flask
import flask_session


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
        if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
            print("Configuring redis to connect to redis-server docker")
            app.config['SESSION_REDIS'] = redis.from_url('redis://redis-server:6379')
        else:
            print("Configuring redis to connect to localhost")
            app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

    if flask_session_type=="mongodb":
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

