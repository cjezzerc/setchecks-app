import os

from flask import Flask
import flask_session

import redis

def create_app(test_config=None, use_flask_session_and_redis=False):
    print(test_config)
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    
    app.secret_key = 'BAD_SECRET_KEY'

# Configure Redis for storing the session data on the server-side
    if use_flask_session_and_redis: # stores session in redis rather than in cookie
                                    # cookie will just contain a session id
                                    # all this is handled by flask-session and redis
        # for this needs redis docker running via:
        # docker run --name some-redis -d -p 6379:6379 redis
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
        server_session = flask_session.Session(app) # resets session variable behaviour so uses redis
    
    
    from . import vsmt_uprot_app
    app.register_blueprint(vsmt_uprot_app.bp)

    
    return app




# def OLD_create_app(test_config=None):
#     print(test_config)
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'rsviewer.sqlite'),
#     )

#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
        
#         # load the test config if passed in
#         app.config.from_mapping(test_config)

#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass

#     # a simple page that says hello
#     @app.route('/hello')
#     def hello():
#         return 'Hello, World!'

#     # from . import db
#     # db.init_app(app)
    
#     from . import vsmt_uprot_app
#     app.register_blueprint(vsmt_uprot_app.bp)

#     # from . import blog
#     # app.register_blueprint(blog.bp)
#     # app.add_url_rule('/', endpoint='index')

#     return app
