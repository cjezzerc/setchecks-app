"""Utilities (independent of FHIR or Terminology Server) for dealing with SNOMED CT items """

import re

def parse_and_validate_sctid(sctid=None, check_namespace_validity=False):
    """Parse a supplied SCTID into its components, validating as go along
    """    
    
    valid=True
    validation_message="SCTID is valid. Note the validity checks do not test for the presence of this SCTID in a release"
    check_digit=None
    partition_identifier=None
    namespace_identifier=None
    item_identifier=None

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
        if type(sctid)!= str:
            valid=False
            validation_message="The supplied SCTID is of type %s but a string is required." % type(sctid)
            break
        #                                 #
        ###################################

                
        ##################################
        #    Check input is not ""       #
        if sctid== "":
            valid=False
            validation_message="The supplied SCTID is a null string."
            break
        #                                 #
        ###################################

        len_sctid=len(sctid)

        ########################################
        #    Check sctid is decimal digits     #
        if (re.search(r'^[0-9]+$', sctid )) is None:
            valid=False
            validation_message="A SCTID can only contain the digits 0-9 and no other characters (including spaces). The supplied SCTID was '%s'." % sctid
            break
        #                                      #
        ########################################

        ##################################
        #       Check length is >=6      #
        if len_sctid<6:
            valid=False
            validation_message="The supplied SCTID is too short. It has a length of %s but the minimum required length is 6" % len_sctid
            break
        #                                #
        ##################################

        ####################################
        #       Check length is <=18       #
        if len_sctid>18:
            valid=False
            validation_message="The supplied SCTID is too long. It has a length of %s but the maximum allowed length is 18" % len_sctid
            break
        #                                  #
        ####################################

        ########################################
        #       Check no leading zeroes        #
        if sctid[0]=="0":
            valid=False
            validation_message="The supplied SCTID has one or more leading zeroes. This is not allowed."
            break
        #                                      #
        ########################################

        check_digit=sctid[-1]
        
        ##################################
        #     Check the check digit      #
        pass
        #                                #
        ##################################

        partition_identifier=sctid[-3:-1]	
	

        #################################################
        #       Check valid partition identifier        #
        if partition_identifier not in ["00","01","02","10","11","12"]:
            valid=False
            validation_message="The supplied SCTID has a partition identifier of %s. The only allowed values are 00, 01, 02, 10, 11 or 12" % partition_identifier
            break
        #                                               #
        #################################################          

        short_form_flag= partition_identifier in ["00","01","02"]
        long_form_flag=  partition_identifier in ["10","11","12"]

        ###########################################
        # Check length of long form sctid is > 10 #
        if long_form_flag and len_sctid<11:
            valid=False
            validation_message="The supplied SCTID is a 'long form' type. It has a length of %s but the minimum required length for a long form type is 11" % len_sctid
            break
        #                                         #
        ###########################################

        if long_form_flag:
            namespace_identifier=sctid[-10:-3]
        else: 
            namespace_identifier=0

        ######################################################################
        #   Optionally check namespace_identifier is in the published list   #
        if check_namespace_validity:
            pass
        #                                                                    #
        ######################################################################

        if long_form_flag:
            item_identifier=sctid[0:-10]
        else: 
            item_identifier=sctid[0:-3]
        
    print(valid, validation_message, item_identifier, namespace_identifier, partition_identifier, check_digit)
