# Code is conversion of code from:
#     https://github.com/IHTSDO/component-identifier-service-legacy/blob/master/utils/SctIdHelper.js)

FnF = [  # from wikipedia rather than calculated as in original source
    # double checked against other sources
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

Dihedral = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

InverseD5 = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def verhoeff_compute(id_as_string):
    check = 0
    for i in range(len(id_as_string) - 1, -1, -1):
        check = Dihedral[check][FnF[(len(id_as_string) - i) % 8][int(id_as_string[i])]]
    return InverseD5[check]


def verhoeff_check(sctid_string):
    num = sctid_string[:-1]
    supplied_cd = sctid_string[-1]
    computed_cd = str(verhoeff_compute(num))
    return supplied_cd == computed_cd


if __name__ == "__main__":
    import sys

    sctid = sys.argv[1]
    num = sctid[:-1]
    supplied_cd = sctid[-1]
    computed_cd = str(verhoeff_compute(num))
    passes_test = verhoeff_check(sctid)

    print(
        """
        sctid=%s
        num=%s
        supplied cd=%s
        computed cd=%s
        checkdigit passes test: %s"""
        % (sctid, num, supplied_cd, computed_cd, passes_test)
    )
