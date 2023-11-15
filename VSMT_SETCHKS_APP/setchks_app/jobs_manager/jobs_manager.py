import redis
import rq
import rq.job 
import rq.command
# from rq.command import send_shutdown_command

from setchks_app.redis.get_redis_client import get_redis_string

class SetchksJobsManager():
    __slots__=[
    "jobs_running",
    "jobs",
    "redis_connection_string",
    "setchks_session",
    ]

    def __init__(self, setchks_session=None):
        self.jobs_running=False # could become a property based on jobs!=[]
        self.jobs=[]
        self.redis_connection_string=get_redis_string() # use string rather than client so object is hashable
        self.setchks_session=setchks_session
        
    def launch_job(self, setchk=None, setchks_session=None):
        q = rq.Queue(connection=redis.from_url(self.redis_connection_string))
        rq_job = q.enqueue(setchk.run_check, setchks_session=setchks_session)
        self.jobs_running=True
        self.jobs.append(SetchksJob(rq_job=rq_job, associated_task=setchk.setchk_code))
        

    def update_job_statuses(self):
        self.jobs_running=False # this will set back to True if finds any jobs running/queued below
        for setchks_job in self.jobs:
            if setchks_job.status not in ["finished","failed"]: # i.e. if we do not yet know if it has finished/failed
                rq_job_id=setchks_job.rq_job_id
                rq_job = rq.job.Job.fetch(rq_job_id, connection=redis.from_url(self.redis_connection_string))
                rq_status=rq_job.get_status()
                if rq_status=="finished":
                    if setchks_job.associated_task[:3]=="CHK":
                        self.setchks_session.setchks_results[setchks_job.associated_task]=rq_job.result
                        setchks_job.results_fetched=True
                elif rq_status=="failed":
                    pass # no specific action but setchks_job_status will pick this up     
                else: # still running or queued
                    self.jobs_running=True
                setchks_job.status=rq_status
        return self.repr_job_statuses()


        #     try:
        #         func=rq_job.func_name
        #         enqueued_at=str(rq_job.enqueued_at)[:16]
        #         started_at=str(rq_job.started_at)[:16]
        #         ended_at=str(rq_job.ended_at)[:16]
        #         data.append(f'{rq_job.id} {status:10} q:{enqueued_at}  s:{started_at}  e:{ended_at} {func} ')
        #     except:
        #         data.append(f'{rq_job.id} {status:10} no more data available ')
        # return data
    
    def kill_all_jobs(self):
        pass

    def repr_job_statuses(self):
        if self.jobs_running:
            output_strings=["Jobs are still running:"]
        else:
            output_strings=["No jobs are still running:"]

        for setchks_job in self.jobs:
            output_strings.append(f"{setchks_job.rq_job_id} {setchks_job.status}")
        return output_strings

class SetchksJob():
    __slots__=[
    "rq_job_id",
    "associated_task",
    "status",
    "results_fetched",
    ]
    def __init__(self, 
                 rq_job=None,
                 associated_task=None):
        self.rq_job_id=rq_job.id
        self.associated_task=associated_task
        self.status=None
        self.results_fetched=False