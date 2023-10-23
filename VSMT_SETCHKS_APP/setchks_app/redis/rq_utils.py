
import os, time

import logging
logger=logging.getLogger()
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)

from rq import Queue
from rq.job import Job
from rq.command import send_shutdown_command
from rq.worker import Worker

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

def kill_all_rq_workers():
    logger.debug("Killing all rq workers")
    redis = get_redis_client()
    workers = Worker.all(redis)
    for worker in workers:
        send_shutdown_command(redis, worker.name)  # Tells worker to shutdown

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

def job_stack_trace(job_id=None):
    redis_connection=get_redis_client()
    job=Job.fetch(job_id, connection=redis_connection)
    return job.exc_info.split('/n')

def job_result(job_id=None):
    redis_connection=get_redis_client()
    job=Job.fetch(job_id, connection=redis_connection)
    return job.result

def jobs():
    redis_connection=get_redis_client()
    q = Queue(connection=redis_connection)
    
    data=[]
    job_ids_in_queue = q.job_ids
    job_ids_started = q.started_job_registry.get_job_ids()
    job_ids_finished = q.finished_job_registry.get_job_ids()
    job_ids_failed = q.failed_job_registry.get_job_ids()
    for job_id in job_ids_in_queue+job_ids_started+job_ids_finished+job_ids_failed:
        job = Job.fetch(job_id, connection=redis_connection)
        status=job.get_status()
        try:
            func=job.func_name
            kwargs=job.kwargs
            enqueued_at=str(job.enqueued_at)[:16]
            started_at=str(job.started_at)[:16]
            ended_at=str(job.ended_at)[:16]
            # data.append(f'{job_id} {status:10} ')
            data.append(f'{job_id} {status:10} q:{enqueued_at}  s:{started_at}  e:{ended_at} {func} {kwargs} ')
        except:
            data.append(f'{job_id} {status:10} no more data available ')

    return data



# job.get_status(refresh=True) Possible values are queued, started, deferred, finished, stopped, scheduled, canceled and failed. If refresh is True fresh values are fetched from Redis.
# job.get_meta(refresh=True) Returns custom job.meta dict containing user stored data. If refresh is True fresh values are fetched from Redis.
# job.origin queue name of this job
# job.func_name
# job.args arguments passed to the underlying job function
# job.kwargs key word arguments passed to the underlying job function
# job.result stores the return value of the job being executed, will return None prior to job execution. Results are kept according to the result_ttl parameter (500 seconds by default).
# job.enqueued_at
# job.started_at
# job.ended_at
# job.exc_info stores exception information if job doesn’t finish successfully.
# job.last_heartbeat the latest timestamp that’s periodically updated when the job is executing. Can be used to determine if the job is still active.
# job.worker_name returns the worker name currently executing this job.
    
def launch_sleep_job():
    redis_connection=get_redis_client()
    q = Queue(connection=redis_connection)
    result = q.enqueue(rq_dummy_sleep_job, sleep_time=30)
    return result

def rq_dummy_sleep_job(sleep_time=None):
    time.sleep(sleep_time)

def report_on_env_vars():
    output_strings=['open values:']
    for env_var in ['DEPLOYMENT_ENV', 'ONTOSERVER_INSTANCE', 'ONTOAUTH_INSTANCE']:
        output_strings.append(f'{env_var:20}: {os.environ[env_var]}' )
    output_strings.append('secrets exist:')
    for env_var in ['ONTOSERVER_USERNAME', 'ONTOSERVER_SECRET', 'TRUDAPIKEY', 'DOCUMENTDB_USERNAME', 'DOCUMENTDB_PASSWORD']:
        output_strings.append(f'{env_var:20}: {env_var in os.environ}' )
    return output_strings                    
                    
def launch_report_on_env_vars():
    redis_connection=get_redis_client()
    q = Queue(connection=redis_connection)
    result = q.enqueue(report_on_env_vars)
    return result
