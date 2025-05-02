#####################################
#####################################
##     enter metadata endpoint     ##
#####################################
#####################################

import logging
from flask import request, session, render_template

from setchks_app.gui import gui_setchks_session
from setchks_app.identity_mgmt.wrapper import auth_required
from setchks_app.gui.breadcrumbs import Breadcrumbs
from setchks_app.sct_versions import graphical_timeline

@auth_required
def enter_metadata():
    setchks_session=gui_setchks_session.get_setchk_session(session)
    setchks_session.set_sct_versions() # this is belt and braces for case where extra sct
                                       # versions loaded suring a session
    
    current_sct_version=setchks_session.sct_version # remember this in case changes in next sections
    current_sct_version_b=setchks_session.sct_version_b # remember this in case changes in next sections

    # if reach here via click on save name and purpose button
    if 'vs_name' in request.form:
        setchks_session.vs_name=request.form['vs_name']
        setchks_session.vs_purpose=request.form['vs_purpose']
    

    # if reach here via click on versions dropdown
    if 'select_sct_version' in request.form:
        # print("===>>>>", request.form['select_sct_version'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['select_sct_version'])-1]
    
    # if reach here via click on versions timeline
    if 'pointNumber' in request.form:
        print("===>>>> pointNumber=", request.form['pointNumber'])
        setchks_session.sct_version=setchks_session.available_sct_versions[int(request.form['pointNumber'])]

       # if reach here via click on versions dropdown (b)
    if 'select_sct_version_b' in request.form:
        # print("===>>>>", request.form['select_sct_version'])
        setchks_session.sct_version_b=setchks_session.available_sct_versions[int(request.form['select_sct_version_b'])-1]
    
    # if reach here via click on versions timeline (b)
    if 'pointNumber_b' in request.form:
        # print("===>>>> pointNumber=", request.form['pointNumber'])
        setchks_session.sct_version_b=setchks_session.available_sct_versions[int(request.form['pointNumber_b'])]

    if 'data_entry_extract_type' in request.form:
        setchks_session.data_entry_extract_type=request.form['data_entry_extract_type']
        setchks_session.reset_analysis() # throw away all old results

    if 'output_full_or_compact' in request.form:
        setchks_session.output_full_or_compact=request.form['output_full_or_compact']

    if 'sct_version_mode' in request.form:   
        setchks_session.sct_version_mode=request.form['sct_version_mode']
        setchks_session.reset_analysis() # throw away all old results

    if setchks_session.sct_version!=current_sct_version: # if have changed sct_version
        setchks_session.reset_analysis() # throw away all old results
    
    if setchks_session.sct_version_b!=current_sct_version_b: # if have changed sct_version_b
        setchks_session.reset_analysis() # throw away all old results


    timeline_data_json, timeline_layout_json, timeline_info_json=graphical_timeline.create_graphical_timeline(
        selected_sct_version=setchks_session.sct_version,
        available_sct_versions=setchks_session.available_sct_versions,
        )
    
    if setchks_session.sct_version_mode=="DUAL_SCT_VERSIONS":
        timeline_data_json_b, timeline_layout_json_b, timeline_info_json_b=graphical_timeline.create_graphical_timeline(
        selected_sct_version=setchks_session.sct_version_b,
        available_sct_versions=setchks_session.available_sct_versions,
        )
    else:
        timeline_data_json_b, timeline_layout_json_b, timeline_info_json_b=(None,None,None,)
    
    bc=Breadcrumbs()
    bc.set_current_page("enter_metadata")

    return render_template(
        'enter_metadata.html',
        breadcrumbs_styles=bc.breadcrumbs_styles,
        setchks_session=setchks_session,
        timeline_data_json=timeline_data_json,
        timeline_layout_json=timeline_layout_json,
        timeline_info_json=timeline_info_json,
        timeline_data_json_b=timeline_data_json_b,
        timeline_layout_json_b=timeline_layout_json_b,
        timeline_info_json_b=timeline_info_json_b,
        )