#!/usr/bin/env python
import sys, os

import logging
logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.DEBUG,
)
logger=logging.getLogger(__name__)

sys.path.append('../..')

from setchks_app.concepts_service.concepts_service import ConceptsService

cs=ConceptsService()

action=sys.argv[1]

if action=="check_coverage":
    for k,v in cs.check_whether_releases_on_ontoserver_have_collections().items():
        print(f'{k}: {v}')

if action=="make_missing":
    cs.make_missing_collections()
