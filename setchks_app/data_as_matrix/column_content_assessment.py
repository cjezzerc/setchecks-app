"""class to hold the items such as assessment of number of valid sctids in a list of marshalled row objects"""


class ColumnContentAssessment:

    __slots__ = [
        "n_rows_in_file",
        "n_data_rows",
        "n_valid_sctid_rows",
        "fraction_valid_sctid_rows",
    ]

    def __init__(self):
        n_rows_in_file = None
        self.n_data_rows = None
        self.n_valid_sctid_rows = None
        self.fraction_valid_sctid_rows = None

    def assess(
        self,
        marshalled_rows=None,
    ):
        self.n_rows_in_file = len(marshalled_rows)
        self.count_data_rows(marshalled_rows=marshalled_rows)
        self.count_valid_sctid_rows(marshalled_rows=marshalled_rows)
        if self.n_data_rows > 0:
            self.fraction_valid_sctid_rows = self.n_valid_sctid_rows / self.n_data_rows

    def count_data_rows(
        self,
        marshalled_rows=None,
    ):
        self.n_data_rows = 0
        for mr in marshalled_rows:
            if not mr.blank_row:
                self.n_data_rows += 1

    def count_valid_sctid_rows(
        self,
        marshalled_rows=None,
    ):
        self.n_valid_sctid_rows = 0
        for mr in marshalled_rows:
            if mr.C_Id_entered or mr.D_Id_entered:
                self.n_valid_sctid_rows += 1
