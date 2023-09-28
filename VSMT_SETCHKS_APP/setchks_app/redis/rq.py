
import os, time

import logging
logger=logging.getLogger()
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)

from rq import Queue

from setchks_app.redis.get_redis_client import get_redis_string, get_redis_client

def start_rq_worker():
    redis_string=get_redis_string()
    logger.debug("About to start rq worker")
    os.system(f"rq worker --url '{redis_string}' &")
    logger.debug("Started rq worker")
    response=os.popen("rq info").readlines()
    logger.debug(f"response from rq info is {response}")

def count_running_rq_workers():
    redis_string=get_redis_string()
    data=os.popen(f"rq info --only-workers --url '{redis_string}'").readlines()
    logger.debug(data)
    n_workers=int(data[-1].split()[0])
    logger.debug(f"{n_workers} rq workers running")
    return n_workers

def start_rq_worker_if_none_running():
    n_workers=count_running_rq_workers()
    if n_workers==0:
        start_rq_worker()
    else:
        logger.debug(f"Not starting an rq as {n_workers} rq workers apparently running")

def list_rq_workers():
    redis_string=get_redis_string()
    data=os.popen(f"rq info --only-workers --url '{redis_string}'").readlines()

    return data

def get_rq_info():
    redis_string=get_redis_string()
    data=os.popen(f"rq info --url '{redis_string}'").readlines()
    return data

def launch_sleep_job():
    redis_connection=get_redis_client()
    q = Queue(connection=redis_connection)
    result = q.enqueue(rq_dummy_sleep_job, sleep_time=30)
    return result

def rq_dummy_sleep_job(sleep_time=None):
    time.sleep(sleep_time)

