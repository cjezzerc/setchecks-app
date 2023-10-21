from rq import Queue
from rq.job import Job
# from redis import Redis

import logging
logger=logging.getLogger(__name__)

from setchks_app.redis.get_redis_client import get_redis_string, get_redis_client

def run_queued_setchks(setchks_list=None, setchks_session=None):
    logger.debug("Queued list:" + str(setchks_list))
    redis_conn = get_redis_client()
    q = Queue(connection=redis_conn)  # no args implies the default queue
    queued_jobs=[]
    for setchk in setchks_list:
        run_in_rq=False
        if run_in_rq:
            job = q.enqueue(setchk.run_check, setchks_session=setchks_session)
            logger.debug(f"Queued up {setchk.setchk_code} : job_id={job.id}")
            queued_jobs.append((setchk, job.id))
        else:
            logger.debug("Running ..: " + str(setchk.setchk_code))
            setchk.run_check(setchks_session=setchks_session)
    return(queued_jobs)


# from worker_function import count_words_at_url
# import time

# # Tell RQ what Redis connection to use
# redis_conn = Redis()
# q = Queue(connection=redis_conn)  # no args implies the default queue

# # Delay execution of count_words_at_url('http://nvie.com')
# job = q.enqueue(count_words_at_url, 'http://nvie.com')
# print(job.result)   # => None  # Changed to job.return_value() in RQ >= 1.12.0

# # Now, wait a while, until the worker is finished
# while True:
#     time.sleep(2)
#     print(job.result)   # => 889  # Changed to job.return_value() in RQ >= 1.12.0

def get_job_by_id(job_id=None):
    print("====>>>", job_id)
    redis_conn = get_redis_client()
    job = Job.fetch(id=job_id, connection=redis_conn)   
    return job