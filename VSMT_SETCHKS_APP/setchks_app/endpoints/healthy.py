###############################
################################
# Simple health check endpoint #
################################
################################

import logging

logger=logging.getLogger(__name__)

def healthy():
    logger.info("health check called")
    return "Healthy"