#####################################
#####################################
##     rq endpoint                 ##
#####################################
#####################################

import logging
from flask import (
    request, session
)
from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only

from setchks_app.redis.rq_utils import (
    get_rq_info, 
    launch_sleep_job, 
    jobs, 
    job_result, 
    job_stack_trace, 
    report_on_env_vars, 
    launch_report_on_env_vars,
    start_rq_worker_if_none_running, 
    kill_all_rq_workers,
    start_specific_rq_worker,
    )

logger=logging.getLogger(__name__)

@auth_required
@admin_users_only
def rq():
    logger.info("rq called")
    logger.debug(list(request.args.items()))
    action=request.args.get("action", None)
    job_id=request.args.get("job_id", None)
    worker_name=request.args.get("worker_name", None)
    
    setchks_session=gui_setchks_session.get_setchk_session(session)
    
    if action is None:
        output_strings=get_rq_info()
        return '<br>'.join(output_strings)
    
    if action =="launch_sleep_job":
        result=launch_sleep_job()
        result=str(result)[1:-1]
        logger.debug(f'result={result}')
        return result
    
    if action=="app_ev":
        return '<pre>'+'<br>'.join(report_on_env_vars())+'</pre>'
    
    if action=="worker_ev":
        launch_report_on_env_vars()
        return 'Look in logs for output'

    if action =="jobs":
        # return str(jobs())
        return '<pre>'+'<br>'.join(jobs())+'</pre>'
    
    if action=="job_stack_trace":
        return '<pre>'+'<br>'.join(job_stack_trace(job_id=job_id))+'</pre>'
    
    if action=="failed_jobs":
        return_str=""
        for job in setchks_session.setchks_jobs_manager.jobs:
            if job.status=="failed":
                return_str += '<br><pre>'+'<br>'.join(job_stack_trace(job_id=job.rq_job_id))+'</pre>'
        return return_str

    if action=="job_result":
        return '<pre>'+str(job_result(job_id=job_id))+'</pre>'
    
    if action=="setchk_job_result":
        return str(job_result(job_id=job_id).__repr__())

    if action=="restart_worker":
        kill_all_rq_workers()
        start_rq_worker_if_none_running()
        return 'worker restarted'
    
    if action=="start_specific_worker":
        message=start_specific_rq_worker(worker_name=worker_name)
        return message
    
    if action=="kill_all_workers":
        kill_all_rq_workers()
        return 'all worker processes killed'
    
    return f"Did not understand that: {action}"