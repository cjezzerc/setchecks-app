########################################
########################################
# check coverage of data in mongodb    #
########################################
########################################

import logging
from flask import request
from setchks_app.identity_mgmt.wrapper import auth_required, admin_users_only
from setchks_app.descriptions_service.descriptions_service import DescriptionsService
from setchks_app.concepts_service.concepts_service import ConceptsService

logger = logging.getLogger(__name__)


@auth_required
@admin_users_only
def check_coverage():
    logger.info("descriptions_db called")
    logger.debug(list(request.args.items()))
    data_type = request.args.get(
        "data_type", "descriptions"
    )  # alternatives are "hst" or "qt" though "qt" not used currently
    if data_type == "concepts":
        ds = ConceptsService()
    else:
        ds = DescriptionsService(data_type=data_type)

    result = ds.check_whether_releases_on_ontoserver_have_collections()
    output_strings = [f"{x}:{result[x]}" for x in result]
    return "<br>".join(output_strings)
