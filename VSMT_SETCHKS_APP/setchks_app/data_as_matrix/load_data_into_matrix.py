"""function to split up inputted value set into a matrix (list of lists)"""

from setchks_app.data_as_matrix.data_cell_contents import DataCellContents

import logging
logger=logging.getLogger(__name__)

import openpyxl

def load_data_into_matrix(setchks_session, 
                                    data=None, 
                                    upload_method=None, 
                                    table_has_header=None, 
                                    separator="\t"):
        
    setchks_session.table_has_header=table_has_header# True, False or None(==unknown)
    if setchks_session.table_has_header: # ** generally need graceful ways to cope with things like a file that has no data rows etc
        setchks_session.first_data_row=1
    else:
        setchks_session.first_data_row=0 
    if upload_method in ["from_file","from_filename"]: # from_filename only implemented for xlsx due to issue with zip file error
        
        if upload_method=="from_file":
            setchks_session.filename=getattr(data,'filename',None)  # file obj for data passed in via GUI 
                                                                    # seems to have "filename" attribute 
            if setchks_session.filename==None: # whereas if from data=open(file) has "name" 
                setchks_session.filename=getattr(data,'name',None)
        else:
            setchks_session.filename=data
        
        if (len(setchks_session.filename)>=6) and (setchks_session.filename[-5:]=='.xlsx'):
            file_type="xlsx"
        else:
            file_type="other"

        if file_type=="xlsx":
            setchks_session.data_as_matrix=[]
            setchks_session.unparsed_data=None # this was put in for the text file case so could reparse. Reparsing (e.g. for change of delimiter
                                                # is not yet implemented. However reparsing is not relevant for xlsx so probably safe just to
                                                # set this to None
            wb=openpyxl.load_workbook(data)
            ws=wb.worksheets[0]
            for row in ws.iter_rows():
                row_as_list=[]
                for cell in row:
                    row_as_list.append(DataCellContents(cell_contents=cell.value))
                setchks_session.data_as_matrix.append(row_as_list)

        else:
            setchks_session.data_as_matrix=[]
            setchks_session.unparsed_data=data.readlines()
        
            for line in setchks_session.unparsed_data:
                if type(line)==str:
                    decoded_line=line
                else: # decoding seems necessary if file data is passed from Flask app form POST
                    try:
                        decoded_line=str(line, 'utf-8')

                    except: # if second decode fails will currently raise ungraceful exception
                            # Also seems have to test every line as some lines can decode OK with utf-8 but some fail if really
                            # is ISO-8859-1 (e.g. in original culprit file, only line 6 in an 11 line file was not decodable as UTF-8)
                        decoded_line=str(line, 'ISO-8859-1') # this is what Excel seems to want to save tab-delimited files as

                f=decoded_line.split(separator)
                f=[x.strip() for x in f]
                f=[DataCellContents(cell_contents=x) for x in f]
                setchks_session.data_as_matrix.append(f)

            #find maximum width and pad any rows shorter than this with empty content
            nmax=0
            for row in setchks_session.data_as_matrix:
                nmax=max(nmax, len(row))
            for row in setchks_session.data_as_matrix:
                if len(row)<nmax:
                    row+=[DataCellContents(cell_contents="") for x in range(0,nmax-len(row))]




