
def do_check(setchks_session=None, setchk_results=None):
    print("A test check has been called")
    setchk_results.meta_data["Test"]="Has run"
