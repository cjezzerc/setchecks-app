
from openpyxl.utils import get_column_letter
import setchks_app.setchks.setchk_definitions

def make_analysis_by_outcome_sheet(
    ws=None, 
    setchks_list_to_report=None,
    setchks_session=None,
    color_fills=None,
    border=None,
    output_OK_messages=None,
    ): 

    setchks=setchks_app.setchks.setchk_definitions.setchks
    setchks_results=setchks_session.setchks_results

    analysis_by_outcomes_row_numbers_map=[] # each entry in list corresponds 1:1 to a row in data file
                                # each such entry is a dict
                                #        keyed by:setchk code
                                #        value=row number in analysis_by_outcome_sheet that this function constructs 
                                # structure is used so that other sheets can link to the right row on this sheet 

    # simple header row (but only if data matrix had one; need to do this better)
    if setchks_session.table_has_header:
        header_row_cell_contents=[x.string for x in setchks_session.data_as_matrix[0]]
        # ws.append(["Row number", "Check", "Message"] + setchks_session.data_as_matrix[0]) # ** need to create better header row
        ws.append(["","Row specific info","Row number"] + header_row_cell_contents) # ** need to create better header row

    ###################################################################################################
    # first loop over all check items and build a dict so can output them grouped by setchk and outcome
    ###################################################################################################
    check_items_dict={} # will be keyed by setchk_code, then by outcome_code
                        # value will be tuple of  (i_data_row, data_row, check_item,)
    for i_data_row, data_row in enumerate(setchks_session.data_as_matrix[setchks_session.first_data_row:]):
        for setchk_code in setchks_list_to_report:
            if setchk_code not in check_items_dict:
                check_items_dict[setchk_code]={}
            setchk_results=setchks_results[setchk_code]
            if setchk_results.row_analysis!=[]:
                for check_item in setchk_results.row_analysis[i_data_row]:
                    output_OK_messages=True  # TEMPORARY while implementing
                    if output_OK_messages or check_item.outcome_level not in ["INFO","DEBUG"]:
                        outcome_code=check_item.outcome_code
                        if outcome_code not in check_items_dict[setchk_code]:
                            check_items_dict[setchk_code][outcome_code]=[]
                        check_items_dict[setchk_code][outcome_code].append((i_data_row, data_row, check_item,))


    ####################################
    # now loop over dict and make output 
    ####################################
    analysis_by_outcomes_row_numbers_map={} # keyed by outcome_code
                                            # value is dict of data_row:output_sheet_row
    for setchk_code in check_items_dict:
        ws.append([setchks[setchk_code].setchk_short_name])
        ws.append(["----"]) 
        outcome_codes_sorted=sorted(check_items_dict[setchk_code].keys())
        for outcome_code in outcome_codes_sorted:
            analysis_by_outcomes_row_numbers_map[outcome_code]={}
            i_temp, data_row_temp, first_check_item=check_items_dict[setchk_code][outcome_code][0]
            message=f"{outcome_code}:{first_check_item.general_message}"
            ws.append([message])
            for i_data_row, data_row, check_item in check_items_dict[setchk_code][outcome_code]:
                data_row_cell_contents=[x.string for x in data_row]
                input_file_row_number=i_data_row+setchks_session.first_data_row+1
                row_specific_message=check_item.row_specific_message
                if row_specific_message=="None":
                    row_specific_message=""
                ws.append([
                    "",
                    row_specific_message,
                    f"Row{input_file_row_number}",
                    ] 
                    + data_row_cell_contents
                    )
                if i_data_row not in analysis_by_outcomes_row_numbers_map[outcome_code]:
                    analysis_by_outcomes_row_numbers_map[outcome_code][i_data_row]=[] # that this is a list is for the rare case where
                                                                                      # the same outcome code might occur more than once for the same row
                                                                                      # see comment in make_analysis_by_row_sheet.py
                analysis_by_outcomes_row_numbers_map[outcome_code][i_data_row].append(ws.max_row)
            ws.append(["----"]) 
        ws.append(["----"]) 
        ws.append(["----"]) 
    
    # crude cell with setting
    cell_widths=[50,30,10] + [20]*10
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

    ws['A1'].hyperlink="#By_Row!C5"
    return analysis_by_outcomes_row_numbers_map
