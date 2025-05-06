#####################################
#####################################
##    column identities endpoint   ##
#####################################
#####################################

import logging
from flask import request, session, render_template

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.ts_and_cs.wrapper import accept_ts_and_cs_required
from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.data_as_matrix.columns_info import ColumnsInfo
from setchks_app.data_as_matrix.marshalled_row_data import MarshalledRow

logger=logging.getLogger(__name__)

# @bp.route('/column_identities', methods=['GET','POST'])
@auth_required
def column_identities():

    # if not is_authorised(): # @auth_required wrapper did not seem to work here ? issue with request.files?
    #     return redirect('/data_upload')
    
    print(request.form.keys())
    print("REQUEST:",request.args.keys())
    print(request.files)

    setchks_session=gui_setchks_session.get_setchk_session(session)

    # if reach here via file upload, load the data into matrix
    multisheet_flag=False
    too_many_rows=False
    too_few_rows=False
    if 'uploaded_file' in request.files:
        if setchks_session.load_file_behaviour=="DEFAULT_SETTINGS":
            session['setchks_session']=None
            setchks_session=gui_setchks_session.get_setchk_session(session)
        multisheet_flag=setchks_session.load_data_into_matrix(data=request.files['uploaded_file'], upload_method='from_file', table_has_header=True)
        too_many_rows= len(setchks_session.data_as_matrix)>5001
        setchks_session.reset_analysis() # throw away all old results
        setchks_session.marshalled_rows=[]

        if (
            (setchks_session.columns_info==None) 
            or (setchks_session.columns_info.ncols != len(setchks_session.data_as_matrix[0]))
            or (setchks_session.load_file_behaviour=="DEFAULT_SETTINGS")
        ):
            if setchks_session.data_as_matrix != []:
                ci=ColumnsInfo(ncols=len(setchks_session.data_as_matrix[0]))
                setchks_session.columns_info=ci
            else:
                print("!!!!!!!!!!!!!!!!!!!! Too few rows")
                too_few_rows=True

    # if reach here via click on a column identity dropdown
    if len(request.form.keys())!=0:
        k, v=list(request.form.items())[0]
        icol=int(k.split("_")[-1])
        requested_column_type=v
        ci=setchks_session.columns_info
        success_flag, message=ci.set_column_type(icol=icol,requested_column_type=requested_column_type)
        logger.debug("Type change attempt: %s %s %s %s" % (icol, requested_column_type, success_flag, message))
        if success_flag: # if have changed column types (in any way)
            setchks_session.reset_analysis() # throw away all old results
            setchks_session.marshalled_rows=[] # force recalc of marshalled rows

    if not too_many_rows:
        if setchks_session.marshalled_rows==[]:
            for row in setchks_session.data_as_matrix[setchks_session.first_data_row:]: # The marshalled_rows list does NOTinclude the header row
                mr=MarshalledRow(row_data=row, columns_info=setchks_session.columns_info)
                setchks_session.marshalled_rows.append(mr)
            setchks_session.column_content_assessment.assess(marshalled_rows=setchks_session.marshalled_rows)
    else:
        setchks_session.data_as_matrix=[]
        setchks_session.filename=""

    type_labels={"CID":"Concept Id", "DID":"Description Id", "MIXED":"Mixed Id", "DTERM":"Term","OTHER":"Other"}
    if setchks_session.columns_info is not None:
        column_type_labels=[type_labels[x] for x in setchks_session.columns_info.column_types]
    else:
        column_type_labels=None
    rows_processable=[mr.row_processable for mr in setchks_session.marshalled_rows]
    # logger.debug("rows_processable:"+str(rows_processable))

    bc=Breadcrumbs()
    bc.set_current_page("column_identities")
    if too_few_rows is False:
        return render_template('column_identities.html',
                            setchks_session=setchks_session,
                            file_data=setchks_session.data_as_matrix,
                            filename=setchks_session.filename,
                            breadcrumbs_styles=bc.breadcrumbs_styles,
                            rows_processable=rows_processable,
                            column_type_labels=column_type_labels,
                            multisheet_flag=multisheet_flag,
                            too_many_rows=too_many_rows,
                            too_few_rows=too_few_rows,
                                )
    else:
        return render_template('blank_file_alert.html')