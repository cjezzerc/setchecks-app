"""Utilities (independent of FHIR or Terminology Server) for dealing with SNOMED CT items """

import re

class ParsedSCTID:

    __slots__=("sctid_string",
               "underscore_separated_form",
               "valid",
               "validation_message", 
               "short_form_flag",
               "long_form_flag",
               "required_check_digit",
               "check_digit",
               "partition_identifier",
               "namespace_identifier",
               "check_namespace_validity",
               "item_identifier",
               "component_type")

    def __init__(self, *, string=None, check_namespace_validity=False):
        self.sctid_string=string
        self.underscore_separated_form=None
        self.valid=None
        self.validation_message=""
        self.required_check_digit=None
        self.check_digit=None
        self.partition_identifier=None
        self.namespace_identifier=None
        self.check_namespace_validity=check_namespace_validity
        self.item_identifier=None
        self.component_type="Other" # Currently everything that comes out with valid=False will be of type "Other"
                                    # No other analysis done on them
        self.short_form_flag=None
        self.long_form_flag=None

        self.parse_and_validate_sctid()

    def __str__(self):
        output_str=""
        for attribute in self.__slots__:
            output_str+="%20s = %s\n" % (attribute, self.__getattribute__(attribute))
        return(output_str)

    def parse_and_validate_sctid(self):
        """Parse a supplied SCTID into its components, validating as go along
        """    
    
        #first define it to be valid and then all the checks attempt to falsify this
        self.valid=True
        self.validation_message="SCTID is valid. Note the validity checks do not test for the presence of this SCTID in a release"
        
        first_time_round_while=True
        while first_time_round_while: 
            # This while 'loop' only runs once
            first_time_round_while=False

            # A set of validity checks and parsing steps follow.
            # If a particular check fails, a "break" statement exits the 'loop' at that point
            # Each such check is separated out with the use of '####' 'brackets' and has a standard form
            # If the check fails it must always:
            #       set valid to False
            #       set a validation message;
            #       and then 'break'
            # If a check fails then any subsequent parsing steps are not attempted and their corresponding variables remain as None

        
            ##################################
            #    Check input is a string     #
            if type(self.sctid_string)!= str:
                self.valid=False
                self.validation_message="The supplied SCTID is of type %s but a string is required." % type(self.sctid_string)
                break
            #                                 #
            ###################################

                    
            ##################################
            #    Check input is not ""       #
            if self.sctid_string== "":
                self.valid=False
                self.validation_message="The supplied SCTID is a null string."
                break
            #                                 #
            ###################################

            len_sctid=len(self.sctid_string)

            ########################################
            #    Check sctid is decimal digits     #
            if (re.search(r'^[0-9]+$', self.sctid_string )) is None:
                self.valid=False
                self.validation_message="A SCTID can only contain the digits 0-9 and no other characters (including spaces). The supplied SCTID was '%s'." % self.sctid_string
                break
            #                                      #
            ########################################

            ##################################
            #       Check length is >=6      #
            if len_sctid<6:
                self.valid=False
                self.validation_message="The supplied SCTID is too short. It has a length of %s but the minimum required length is 6" % len_sctid
                break
            #                                #
            ##################################

            ####################################
            #       Check length is <=18       #
            if len_sctid>18:
                self.valid=False
                self.validation_message="The supplied SCTID is too long. It has a length of %s but the maximum allowed length is 18" % len_sctid
                break
            #                                  #
            ####################################

            ########################################
            #       Check no leading zeroes        #
            if self.sctid_string[0]=="0":
                self.valid=False
                self.validation_message="The supplied SCTID has one or more leading zeroes. This is not allowed."
                break
            #                                      #
            ########################################

            self.check_digit=self.sctid_string[-1]
            
            ##################################
            #     Check the check digit      #
            pass
            #                                #
            ##################################

            self.partition_identifier=self.sctid_string[-3:-1]	
        

            #################################################
            #       Check valid partition identifier        #
            if self.partition_identifier not in ["00","01","02","10","11","12"]:
                self.valid=False
                self.validation_message="The supplied SCTID has a partition identifier of %s. The only allowed values are 00, 01, 02, 10, 11 or 12" % self.partition_identifier
                break
            #                                               #
            #################################################          

            self.short_form_flag= self.partition_identifier in ["00","01","02"]
            self.long_form_flag=  self.partition_identifier in ["10","11","12"]

            if self.partition_identifier in ["00","10"]:
                self.component_type="Concept_Id"

            if self.partition_identifier in ["01","11"]:
                self.component_type="Description_Id"

            if self.partition_identifier in ["02","12"]:
                self.component_type="Relationship_Id"


            ###########################################
            # Check length of long form sctid is > 10 #
            if self.long_form_flag and len_sctid<11:
                self.valid=False
                self.validation_message="The supplied SCTID is a 'long form' type. It has a length of %s but the minimum required length for a long form type is 11" % len_sctid
                break
            #                                         #
            ###########################################

            if self.long_form_flag:
                self.namespace_identifier=self.sctid_string[-10:-3]
            else: 
                self.namespace_identifier=0

            ######################################################################
            #   Optionally check namespace_identifier is in the published list   #
            if self.check_namespace_validity:
                pass
            #                                                                    #
            ######################################################################

            if self.long_form_flag:
                self.item_identifier=self.sctid_string[0:-10]
            else: 
                self.item_identifier=self.sctid_string[0:-3]
            
        self.underscore_separated_form=str(self.item_identifier)+"_"+str(self.namespace_identifier)+"_"+str(self.partition_identifier)+"_"+str(self.check_digit)
        # print("Message:",validation_message)
        # print("Component type:", component_type)