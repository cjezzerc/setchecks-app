
from openpyxl.utils import get_column_letter

def make_analysis_by_row_sheet(
    ws=None, 
    setchks_list_to_report=None,
    setchks_session=None,
    color_fills=None,
    border=None,
    output_OK_messages=None,
    analysis_by_outcome_row_numbers_map=None,
    ): 

    setchks=setchks_session.available_setchks
    setchks_results=setchks_session.setchks_results

    row_analysis_row_numbers_map=[] # each entry in list corresponds 1:1 to a row in data file
                                # each such entry is a dict
                                #        keyed by:setchk code
                                #        value=row number in row_analysis_sheet that this function constructs 
                                # structure is used so that other sheets can link to the right row on this sheet 

    # simple header row (but only if data matrix had one; need to do this better)
    if setchks_session.table_has_header:
        header_row_cell_contents=[x.string for x in setchks_session.data_as_matrix[0]]
        # ws.append(["Row number", "Check", "Message"] + setchks_session.data_as_matrix[0]) # ** need to create better header row
        ws.append(["Row number", "Check", "Message","Link"] + header_row_cell_contents) # ** need to create better header row

    for i_data_row, data_row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        something_was_output=False
        row_analysis_row_numbers_map.append({})
        current_row_map=row_analysis_row_numbers_map[-1] 
        for setchk_code in setchks_list_to_report:
            setchk_short_name=setchks[setchk_code].setchk_short_name
            setchk_results=setchks_results[setchk_code]
            data_row_cell_contents=[x.string for x in data_row]
            # ws.append([i_data_row+setchks_session.first_data_row+1, setchk_short_name, setchk_results.row_analysis[i_data_row]["Message"]]+data_row_cell_contents)
            for check_item in setchk_results.row_analysis[i_data_row]:
                if output_OK_messages or check_item.outcome_level not in ["INFO","DEBUG"]:
                    row_to_link_to=analysis_by_outcome_row_numbers_map[check_item.outcome_code][i_data_row]
                    message=f"{check_item.outcome_code}:{check_item.general_message}" 
                    hyperlink_cell_contents=f'=HYPERLINK("#By_Outcome!B{row_to_link_to}","X")'
                    # print(f"MESSAGE_CCELL_CONTENTS:{message_cell_contents}")
                    # print(len(message_cell_contents))
                    ws_row_contents=[
                        i_data_row+setchks_session.first_data_row+1, 
                        setchk_short_name, 
                        message,
                        hyperlink_cell_contents,
                        ] 
                    if not something_was_output: # only add the file data for the first outcome line
                        ws_row_contents+=data_row_cell_contents
                    ws.append(ws_row_contents)
                    current_row_map[setchk_code]=ws.max_row
                    something_was_output=True
        if something_was_output:
            ws.append(["----"]) 
    
    # crude cell with setting
    cell_widths=[15,30,50,5,25,50] + [20]*10
    for i, width in enumerate(cell_widths):
        ws.column_dimensions[get_column_letter(i+1)].width=width     

    # example bit of formatting bling
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

    return row_analysis_row_numbers_map
