import os

from flask import Flask
import flask_session

import redis

def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'BAD_SECRET_KEY'

    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    if "VSMT_DOCKER_COMPOSE" in os.environ: # this env var must be set in docker-compose.yaml
        print("Configuring redis to connect to redis-server docker")
        app.config['SESSION_REDIS'] = redis.from_url('redis://redis-server:6379')
    else:
        print("Configuring redis to connect to localhost")
        app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
    server_session = flask_session.Session(app) # resets session variable behaviour so uses redis
    
    from . import setchks_app
    app.register_blueprint(setchks_app.bp)

    return app

