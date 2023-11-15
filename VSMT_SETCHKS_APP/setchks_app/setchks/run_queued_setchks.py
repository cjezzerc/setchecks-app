from rq import Queue
from rq.job import Job
# from redis import Redis
from setchks_app.jobs_manager.jobs_manager import SetchksJobsManager


import logging
logger=logging.getLogger(__name__)

from setchks_app.redis.get_redis_client import get_redis_string, get_redis_client

def run_queued_setchks(setchks_list=None, setchks_session=None, run_in_rq=True):
    setchks_jobs_manager=SetchksJobsManager(setchks_session=setchks_session)
    setchks_session.setchks_jobs_manager=setchks_jobs_manager
    for setchk in setchks_list:
        if run_in_rq:
            setchks_jobs_manager.launch_job(
                setchk=setchk,
                setchks_session=setchks_session,
                )
            job_status_report=setchks_jobs_manager.update_job_statuses()
            logger.debug("\n".join(job_status_report))
        else:
            logger.debug("Running ..: " + str(setchk.setchk_code))
            setchk.run_check(setchks_session=setchks_session)
    return


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

# def get_job_by_id(job_id=None):
#     print("====>>>", job_id)
#     redis_conn = get_redis_client()
#     job = Job.fetch(id=job_id, connection=redis_conn)   
#     return job