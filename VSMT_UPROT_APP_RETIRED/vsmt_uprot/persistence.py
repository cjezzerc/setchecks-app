
import os.path
import pickle
import time

# This module defines a very simple persistence class for use in Flask apps
# user can add attributes to Persistence objects via check_attribute_initialised
# user is reponsible for saving the object for reuse
#
# flags allow for timing and verbosity and default to False

class Persistence():
        
    def __init__(self, filename, timing_report_flag=False, verbose=False, application_initialisation_function=None, reset=False):
        
        if timing_report_flag:
            start_time=time.time()

        if os.path.exists(filename) and reset==False:

            verbose=False              #TEMP WHILE DEBUGGING!!!
            timing_report_flag=True    #TEMP WHILE DEBUGGING!!!
            if verbose:
                print("PERSISTENCE: about to load from", filename)

            fh=open(filename,'rb')
            temp_dict=pickle.load(fh)
            fh.close()

            if verbose:
                print("PERSISTENCE: loaded OK")

            for k,v in temp_dict.items():
                self.__dict__[k]=v
            if verbose:
                print("PERSISTENCE: file loaded OK -", filename)
                print(self)

        else:
            print("PERSISTENCE: file %s does not yet exist (or reset requested) so just initialising object" % filename)
            self.persistence_filename=filename # this will already be set by the above code if file exists
            if application_initialisation_function: # this function can be passed in to do application specific initialisation
                if verbose:
                    print("PERSISTENCE: calling", application_initialisation_function)
                application_initialisation_function(self)
                self.save(verbose=True)

        if timing_report_flag:
            print("PERSISTENCE: __init__ took (in seconds)", time.time()-start_time)
    

    def __repr__(self):

        str_rep_list=[]
        for k,v in self.__dict__.items():
            str_rep_list.append("PERSISTENCE: key=%s: value=%s" % (k,v))
        return "\n".join(str_rep_list) 


    def check_attribute_initialised(self, attr_name, initialise_to):
        
        # This checks if requested attribute exists and if not initialises it.
        # User can call this to make sure is initialised without having to 
        # formally check themselves 

        if attr_name not in self.__dict__:
            self.__dict__[attr_name]=initialise_to
            return False # i.e. it needed to be initialised
        else:
            return True # i.e. it already existed


    def save(self, timing_report_flag=False, verbose=False ):

        if timing_report_flag:
            start_time=time.time()

        if verbose:
            print("PERSISTENCE: about to save to", self.persistence_filename)

        
        ofh=open(self.persistence_filename,'wb')
        pickle.dump(self.__dict__,ofh)
        ofh.close()

        if verbose:
            print("PERSISTENCE: saved OK")

        if timing_report_flag:
            print("PERSISTENCE: save took (in seconds)", time.time()-start_time)

if __name__=="__main__":

    ####################
    # Simple test code #
    ####################

    pf='/tmp/testing_of_refset_viewer_persistent_storage'
    
    print("Doing rm on %s to start from no existing file" % pf)
    os.system("rm %s" % pf)

    # create object from scratch, add an attribute , change attribute, print and save
    session_persistence=Persistence(pf, timing_report_flag=True, verbose=True)
    session_persistence.check_attribute_initialised("show_children_of",[])
    session_persistence.show_children_of.append(123)
    print(session_persistence)
    session_persistence.save(timing_report_flag=True, verbose=True)

    # Now try again as if in different "context"

    print("Deleting persistence object")
    session_persistence=None

    print("Now reloading it")
    session_persistence=Persistence(pf, timing_report_flag=True, verbose=True)

    print("Now try reinitialising show_children of - should have no effect")
    session_persistence.check_attribute_initialised("show_children_of",[])    
    print(session_persistence)

    session_persistence.show_children_of.append(456)
    print(session_persistence)

# Correct response to test code:

# Doing rm on /tmp/testing_of_refset_viewer_persistent_storage to start from no existing file
# PERSISTENCE: file does not exist so initialising object
# PERSISTENCE: __init__ took (in seconds) 0.0003292560577392578
# PERSISTENCE: key=persistence_filename: value=/tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: key=show_children_of: value=[123]
# PERSISTENCE: about to save to /tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: saved OK
# PERSISTENCE: save took (in seconds) 0.0011246204376220703
# Deleting persistence object
# Now reloading it
# PERSISTENCE: about to load from /tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: loaded OK
# PERSISTENCE: file loaded OK - /tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: key=persistence_filename: value=/tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: key=show_children_of: value=[123]
# PERSISTENCE: __init__ took (in seconds) 0.001940011978149414
# Now try reinitialising show_children of - should have no effect
# PERSISTENCE: key=persistence_filename: value=/tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: key=show_children_of: value=[123]
# PERSISTENCE: key=persistence_filename: value=/tmp/testing_of_refset_viewer_persistent_storage
# PERSISTENCE: key=show_children_of: value=[123, 456]

