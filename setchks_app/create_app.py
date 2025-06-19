import os, logging

from flask import Flask
import flask_session

from redis import from_url
from authlib.integrations.flask_client import OAuth

from . import setchecks_app
from setchks_app.redis.get_redis_client import get_redis_string
from setchks_app.redis.rq_utils import (
    kill_all_rq_workers,
    start_specific_rq_worker,
)
from setchks_app.sct_versions import get_sct_versions
from setchks_app.descriptions_service.descriptions_service import DescriptionsService


logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(setchecks_app.bp)

    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.wrappers import Response

    app.wsgi_app = DispatcherMiddleware(
        Response("Not Found", status=404), {"/TEST123": app.wsgi_app}
    )

    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=os.environ["AUTH0_CLIENT_ID"],
        client_secret=os.environ["AUTH0_CLIENT_SECRET"],
        client_kwargs={
            "scope": "openid profile email offline_access",
        },
        server_metadata_url=f'https://{os.environ["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
    )
    app.config["oauth"] = oauth

    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    redis_connection = from_url(get_redis_string())
    app.config["SESSION_REDIS"] = redis_connection
    server_session = flask_session.Session(
        app
    )  # resets session variable behaviour so uses redis

    app.secret_key = os.environ["FLASK_APP_SECRET"]

    kill_all_rq_workers()
    start_specific_rq_worker(worker_name="worker_long_jobs")
    start_specific_rq_worker(worker_name="worker_short_jobs")

    # Get Git commit and "cleanness" NB Hot code changes will require restart
    # cleanness check not 100% reliable under WSL; sometimes seems sensitive to the line ending issue
    # and reports many files as modified though they are not. But seems erratic.
    app.config["VERSION"] = (
        os.popen("git log --format=%h --abbrev=8 -n 1").readlines()[0].strip()
    )
    git_status_output = os.popen("git status --short").readlines()
    logger.debug(f"git_status_output={str(git_status_output)}")
    if git_status_output != []:
        app.config["VERSION"] += "(modified)"

    if os.environ["DEPLOYMENT_ENV"] == "AWS":
        app.config["ENVIRONMENT"] = os.environ[
            "ENV"
        ].upper()  # just used in Jinja template
    else:
        app.config["ENVIRONMENT"] = "LOCAL"

    ds = DescriptionsService(data_type="hst")
    app.config["sct_versions_available_in_app"] = (
        get_sct_versions.get_sct_versions_available_in_app(descriptions_service=ds)
    )

    return app
