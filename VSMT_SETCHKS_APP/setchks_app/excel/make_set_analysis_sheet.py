

from openpyxl.utils import get_column_letter
import setchks_app.setchks.setchk_definitions


def make_set_analysis_sheet(
    ws=None, 
    setchks_list_to_report=None,
    setchks_session=None,
    color_fills=None,
    border=None,
    ):

    setchks=setchks_app.setchks.setchk_definitions.setchks
    setchks_results=setchks_session.setchks_results

    ws.title='Set analyses'

    # simple header row
    ws.append(["Check", "Message"])

    # Add the set level messages from each check on first sheet
    for setchk_code in setchks_list_to_report:
        setchk_short_name=setchks[setchk_code].setchk_short_name
        for message in setchks_results[setchk_code].set_analysis["Messages"]:
            ws.append([setchk_short_name, message])
            # cell=ws[ws.max_row][0]
            # cell=ws[ws.max_row][1]
        for set_level_table_row in setchks_results[setchk_code].set_level_table_rows:
            ws.append([setchk_short_name, "", set_level_table_row.descriptor, set_level_table_row.value])
        ws.append(["----"]) 
    
    # crude cell with setting
    cell_widths=[30,100,100,30]
    for i, width in enumerate(cell_widths):
        ws.column_dimensions[get_column_letter(i+1)].width=width     

    irow=0
    for row in ws.iter_rows():
        irow+=1
        divider_line=row[0].value=="----"
        for cell in row:
            cell.alignment=cell.alignment.copy(wrap_text=True, vertical='top')
            # if cell.column_letter in ["A","B","C"] or divider_line:
            if divider_line:
                cell.fill=color_fills["grey"]
                cell.border = border  
                ws.row_dimensions[irow].height = 3
