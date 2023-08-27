"""Class to hold current breadcrumbs setting"""
import logging
logger=logging.getLogger(__name__)

class Breadcrumbs():
    __slots__={"breadcrumbs_styles", "page_names"}
    def __init__(self):
        self.page_names=["data_upload", "confirm_upload", "column_identities", "set_metadata", "run_setchecks"]

        self.breadcrumbs_styles={}
        for page_name in self.page_names:
            self.breadcrumbs_styles[page_name]="weak"
                               
    def set_current_page(self, current_page_name=None):
        logger.debug("called")
        if  current_page_name not in self.page_names:
            logger.error("page_name %s value is not valid" % current_page_name)
        else:
            for page_name in self.page_names:
                if page_name==current_page_name: 
                    self.breadcrumbs_styles[page_name]="strong"
                else:
                    self.breadcrumbs_styles[page_name]="weak"
        logger.debug(str(self.breadcrumbs_styles))
        
    