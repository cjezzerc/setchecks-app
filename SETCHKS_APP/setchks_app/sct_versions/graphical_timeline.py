""" graphical clickable display of timeline of releases available"""

import plotly.graph_objects as go
import json

import logging
logger=logging.getLogger(__name__)

def create_graphical_timeline(
    selected_sct_version=None,
    available_sct_versions=None,
    ):

    available_sct_dates=[x.date_string for x in available_sct_versions]
    selected_sct_date=selected_sct_version.date_string
    selected_flags=[(x==selected_sct_date) for x in available_sct_dates]
    
    year0=2022.0
    month0=1.0
    day0=1.0

    x_list=[]
    y_list=[]

    for sct_date in available_sct_dates:
        year=int(sct_date[0:4])
        month=int(sct_date[4:6])
        day=int(sct_date[6:])
        x=(year-year0)*12+(month-month0)+(day-day0)/31.0
        y=0.5
        x_list.append(x)
        y_list.append(y)

    fig=go.Figure ()
        
    fig.update_layout(
        # title="SCT timeline",
      
        )

    fig.update_xaxes(
        dtick=1,
        showgrid=False,
        range=[0.0,24.0],
        tickfont={'size':5,}
        )

    fig.update_yaxes(
        visible=False,
        )

    selected_color    ='Red'
    not_selected_color='LightSkyBlue'
    color_list=[]
    for i_date, flag in enumerate(selected_flags):
        if flag:
            color_list.append(selected_color)
        else:
            color_list.append(not_selected_color)

    marker=dict(color=color_list, size=10, line=dict(color='MediumPurple', width=2))

    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=x_list,
            y=y_list,
            marker=marker,
            showlegend=False,
            hoverinfo="none",
        )
    )

    fig.layout.template=None

    data_json=json.dumps(fig.to_dict()['data'])
    layout_json=json.dumps(fig.to_dict()['layout'])

    timeline_info_json=json.dumps(available_sct_dates)

    return data_json, layout_json, timeline_info_json


