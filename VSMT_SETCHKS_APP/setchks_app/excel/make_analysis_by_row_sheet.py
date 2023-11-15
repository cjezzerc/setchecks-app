
from openpyxl.utils import get_column_letter

def make_analysis_by_row_sheet(
    ws=None, 
    setchks_list_to_report=None,
    setchks_session=None,
    color_fills=None,
    border=None,
    output_OK_messages=None,
    analysis_by_outcome_row_numbers_map=None,
    supp_tabs_row_numbers_map=None,
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
        ws.append(["Row number", "Check", "Message","Link","Supp tab link"] + header_row_cell_contents) # ** need to create better header row

    for i_data_row, data_row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        something_was_output=False
        row_analysis_row_numbers_map.append({})
        current_row_map=row_analysis_row_numbers_map[-1] 
        for setchk_code in setchks_list_to_report:
            setchk_short_name=setchks[setchk_code].setchk_short_name
            setchk_results=setchks_results[setchk_code]
            if setchk_code in supp_tabs_row_numbers_map: # i.e. there is a supp tab for this check
                supp_tab_ws, supp_tab_mapping=supp_tabs_row_numbers_map[setchk_code]
                # print(f"supp_tab_mapping:{supp_tab_mapping}")
            else:
                supp_tab_ws=None        
            data_row_cell_contents=[x.string for x in data_row]
            # ws.append([i_data_row+setchks_session.first_data_row+1, setchk_short_name, setchk_results.row_analysis[i_data_row]["Message"]]+data_row_cell_contents)
            outcome_codes_count={} # this is used to make sure that in the case where the same outcome_code
                                   # can occur more than once for the same row (e.g. where checking for unreccomended tl-hierarchies
                                   # and the concept is in more than one tl-hierarchy then) then the hyperlink fgoes to the
                                   # correct row of the "by outcome" table
                                   # this has been implemented but not thoroughly tested yet! 
            if setchk_results.row_analysis!=[]:
                for check_item in setchk_results.row_analysis[i_data_row]:
                    if output_OK_messages or check_item.outcome_level not in ["INFO","DEBUG"]:
                        outcome_code=check_item.outcome_code
                        if outcome_code not in outcome_codes_count:
                            outcome_codes_count[outcome_code]=0
                        else:
                            outcome_codes_count[outcome_code]+=1
                        row_to_link_to=analysis_by_outcome_row_numbers_map[outcome_code][i_data_row][outcome_codes_count[outcome_code]]
                        message=f"{outcome_code}:{check_item.general_message}" 
                        hyperlink_cell_contents=f'=HYPERLINK("#By_Outcome!B{row_to_link_to}","X")'
                        # print(f"i_data_row: {i_data_row} supp_tab_ws: {supp_tab_ws}")
                        if supp_tab_ws is not None:
                            # print(f"supp_tab_mapping:{supp_tab_mapping} {i_data_row} {supp_tab_mapping[i_data_row]}")    
                            if supp_tab_mapping[i_data_row] is not None:
                                row_to_link_to=supp_tab_mapping[i_data_row]
                                # print(f"row_to_link_to {i_data_row} {row_to_link_to}")
                                supp_tab_hyperlink_cell_contents=f'=HYPERLINK("#{supp_tab_ws.title}!A{row_to_link_to}","S")'
                            else:
                                supp_tab_hyperlink_cell_contents=""
                        else:
                            supp_tab_hyperlink_cell_contents=""

                        # print(f"MESSAGE_CCELL_CONTENTS:{message_cell_contents}")
                        # print(len(message_cell_contents))
                        ws_row_contents=[
                            i_data_row+setchks_session.first_data_row+1, 
                            setchk_short_name, 
                            message,
                            hyperlink_cell_contents,
                            supp_tab_hyperlink_cell_contents,
                            ] 
                        if not something_was_output: # only add the file data for the first outcome line
                            ws_row_contents+=data_row_cell_contents
                        ws.append(ws_row_contents)
                        current_row_map[setchk_code]=ws.max_row
                        something_was_output=True
        if something_was_output:
            ws.append(["----"]) 
    
    # crude cell with setting
    cell_widths=[15,30,50,5,5,25,50] + [20]*10
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
