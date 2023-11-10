class ChkSpecificSheet():
    __slots__=[
        "rows",
        "col_widths"
        ]
    def __init__(self):
        self.rows=[]
        self.col_widths=[]

    def new_row(self): # add a row and return that row to caller
        row=ChkSpecificSheetRow()
        self.rows.append(row)
        return row

class ChkSpecificSheetRow():
    __slots__=[
        "cell_contents",
        "row_height",
        "row_fill",
        "row_formatting"
        ]
    def __init__(self):
        self.cell_contents=[""]
        self.row_height=None
        self.row_fill=None
        self.row_formatting=None