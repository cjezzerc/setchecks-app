from . import checkdigit


def check_if_in_release(sctid=None, ds=None, sct_version=None):
    print(sctid)
    if sctid[-2] == "0":
        data = ds.get_data_about_concept_id(
            concept_id=sctid,
            date_string=sct_version,
        )
        print(data)
        return (
            data != []
        )  # data about a concept id is a list of possible description ids
    elif sctid[-2] == "1":
        data = ds.get_data_about_description_id(
            description_id=sctid,
            date_string=sct_version,
        )
        print(data)
        return (
            data is not None
        )  # data about a description id is a single possible concept id
    else:
        return False


def detect_corruption_and_restore_id(sctid=None, ds=None, sct_version=None):

    sctid = str(sctid)  # in case test with an int

    # can't be excel corruption if not 16, 17 or 18 digits
    n_digits = len(sctid)
    if n_digits < 16 or n_digits > 18:
        return False, None, None, None, None

    # excel corruption will zero the trailing 1, 2 or 3 digits
    trailing_zeroes = (
        (n_digits == 16 and sctid[-1] == "0")
        or (n_digits == 17 and sctid[-2:] == "00")
        or (n_digits == 18 and sctid[-3:] == "000")
    )
    # so if not seen it cannot be corrupted
    if not trailing_zeroes:
        return False, None, None, None, None

    exists_in_release = check_if_in_release(sctid=sctid, sct_version=sct_version, ds=ds)

    # if it exists in release, assume not corrupted
    # (In theory could report if is one of rare cases where the corrupted form is also an sctid in the release)
    if exists_in_release:
        return False, None, None, None, None

    # if cd_ok perhaps could report that might be from another namespace
    # but not implementing now
    # cd_ok=checkdigit.verhoeff_check(sctid)

    # reconstruct as concept_id (RC) or description_id(RD)
    if n_digits == 16:
        temp = sctid[:-1]
        RC = temp + str(checkdigit.verhoeff_compute(temp))
        RD = None
    elif n_digits == 17 or (
        n_digits == 18 and sctid[:6] == "900000"
    ):  # 17 digit or 18 digit "short form" that all seem to start 900000
        temp = sctid[:-2]
        RC = temp + "0" + str(checkdigit.verhoeff_compute(temp + "0"))
        RD = temp + "1" + str(checkdigit.verhoeff_compute(temp + "1"))
    else:  # 18 digits long form
        temp = sctid[:-3]
        RC = temp + "10" + str(checkdigit.verhoeff_compute(temp + "10"))
        RD = temp + "11" + str(checkdigit.verhoeff_compute(temp + "11"))

    RC_in_release = check_if_in_release(sctid=RC, sct_version=sct_version, ds=ds)
    RD_in_release = (RD is not None) and check_if_in_release(
        sctid=RD, sct_version=sct_version, ds=ds
    )

    return True, RC, RD, RC_in_release, RD_in_release
