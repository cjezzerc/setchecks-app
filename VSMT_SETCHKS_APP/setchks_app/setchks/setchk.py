
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
    __slots__=[
        "setchk_code",
        "setchk_short_name",
        "setchk_function",
        "setchk_data_entry_extract_types",
        ]

    def __init__(
        self, 
        setchk_code=None, 
        setchk_short_name=None, 
        setchk_function=None,
        setchk_data_entry_extract_types=None,
        ):
        """
        Parameters
        ----------
        TBC
        """
        self.setchk_code=setchk_code
        self.setchk_short_name=setchk_short_name
        self.setchk_function=setchk_function
        self.setchk_data_entry_extract_types=setchk_data_entry_extract_types


    def run_check(self,  setchks_session=None):
        """Runs the actual check

        Parameters
        ----------
        setchk_session: VsCheckSession, mandatory
        """
        setchk_results=SetchkResults()
        setchk_results.setchk_code=self.setchk_code
        self.setchk_function(setchks_session=setchks_session, setchk_results=setchk_results)
        setchks_session.setchks_results[self.setchk_code]=setchk_results
        return setchk_results
        # return ("Setcheck %s has been run" % self.setchk_short_name)

