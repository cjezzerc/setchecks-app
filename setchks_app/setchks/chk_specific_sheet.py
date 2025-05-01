class ChkSpecificSheet():
    __slots__=[
        "rows",
        "col_widths",
        "sheet_name",
        "filter_row",
        ]
    def __init__(self, sheet_name=None):
        self.rows=[]
        self.col_widths=[]
        self.sheet_name=sheet_name
        self.filter_row=None

    def new_row(self): # add a row and return that row to caller
        row=ChkSpecificSheetRow()
        self.rows.append(row)
        return row

class ChkSpecificSheetRow():
    __slots__=[
        "cell_contents",
        "row_height",
        "row_fill",
        "row_formatting",
        "is_end_of_clause",
        ]
    def __init__(self):
        self.cell_contents=[""]
        self.row_height=None
        self.row_fill=None
        self.row_formatting=None
        self.is_end_of_clause=None