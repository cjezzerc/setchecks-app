
from openpyxl.utils import get_column_letter
from . import styling


def make_chk_specific_sheets(
    wb=None,
    first_i_ws=None, 
    setchks_list_to_report=None,
    setchks_session=None,
    color_fills=None,
    border=None,
    ):

    i_ws=first_i_ws-1
    for setchk_code in setchks_list_to_report:
        setchk_results=setchks_session.setchks_results[setchk_code]
        if setchk_results.chk_specific_sheet is not None:
            i_ws+=1
            ws=wb.worksheets[i_ws]
            ws.title=f"{setchk_code}_s"
            make_one_chk_specific_sheet(
                ws=ws,
                setchk_code=setchk_code,
                setchk_results=setchk_results,
                color_fills=color_fills,
                border=border,
                )

def make_one_chk_specific_sheet(
    ws=None,
    setchk_code=None,
    setchk_results=None,
    color_fills=None,
    border=None,
    ):

    chk_specific_sheet=setchk_results.chk_specific_sheet

    current_ws_row=0
    for chk_specific_row in chk_specific_sheet.rows:
        # print(chk_specific_row.row_fill, chk_specific_row.row_height, chk_specific_row.cell_contents)
        ws.append(chk_specific_row.cell_contents)
        current_ws_row+=1
        if chk_specific_row.row_height is not None:
            pass
            ws.row_dimensions[current_ws_row].height = chk_specific_row.row_height
        for cell in ws[current_ws_row]:
            # cell.alignment=cell.alignment.copy(wrap_text=True)
            if chk_specific_row.row_fill is not None:
                cell.style=styling.vsmt_style_grey_row # only grey available as stopgap measure
                # cell.fill=color_fills[chk_specific_row.row_fill]
            else:
                cell.style=styling.vsmt_style_wrap_top 

    for i, width in enumerate(chk_specific_sheet.col_widths):
        ws.column_dimensions[get_column_letter(i+1)].width=width     

