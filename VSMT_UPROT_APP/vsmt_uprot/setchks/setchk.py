
from .setchk_results import SetchkResults

class Setchk():
    """A class used to represent a particular type of value set check.

    This class provides a uniform interface for running a particular check.
    It contains not only a reference to the function that runs the check 
    but could perhaps also contain methods for dealing with interrelationships between checks, 
    or anything that shoudl be ensured has been run before a check can run.
    This means that the check function itself can make certain assumptions.

    A SetChk object does not contain any information about a particular occasion
    on which the check is run, thus e.g. .run_check must be supplied with a 
    setchks_session object
    """
    def __init__(self, setchk_name=None, setchk_function=None):
        """
        Parameters
        ----------
        TBC
        """
        self.setchk_name=setchk_name
        self.setchk_function=setchk_function

    def run_check(self,  setchks_session=None):
        """Runs the actual check

        Parameters
        ----------
        setchk_session: VsCheckSession, mandatory
        """
        setchk_results=SetchkResults()
        setchk_results.setchk_name=self.setchk_name
        self.setchk_function(setchks_session=setchks_session, setchk_results=setchk_results)
        setchks_session.setchks_results[self.setchk_name]=setchk_results
        return ("Setcheck %s has been run" % self.setchk_name)

