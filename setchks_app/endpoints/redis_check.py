#################################
#################################
# Simple redis endpoint #
#################################
#################################

import os, datetime, logging
from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only
from setchks_app.redis.get_redis_client import get_redis_client

logger = logging.getLogger(__name__)


@auth_required
@admin_users_only
def redis_check():
    logger.debug("Redis check called")

    import redis

    redis_connection = get_redis_client()
    redis_ping = redis_connection.ping()
    redis_connection.set(
        "mykey", str(datetime.datetime.now().strftime("%d_%b_%Y__%H_%M_%S"))
    )
    time_value = redis_connection.get("mykey")

    return f"redis check:  ping={redis_ping}  stored_date={time_value}"
