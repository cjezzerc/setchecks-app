"""function to split up inputted value set into a matrix (list of lists)"""

from vsmt_uprot.setchks.data_as_matrix.data_cell_contents import DataCellContents

import logging
logger=logging.getLogger(__name__)

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
    if upload_method=="from_text_file":
        setchks_session.filename=data.filename
        setchks_session.data_as_matrix=[]
        setchks_session.unparsed_data=data.readlines()
        for line in setchks_session.unparsed_data:
            if type(line)==str:
                decoded_line=line
            else: # this seems to work if file data is passed from Flask app form POST
                decoded_line=str(line, 'utf-8')
            f=decoded_line.split(separator)
            f=[x.strip() for x in f]
            f=[DataCellContents(cell_contents=x) for x in f]
            setchks_session.data_as_matrix.append(f)



