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
    
    year0=2022
    month0=1
    day0=1

    x_list=[]
    y_list=[]

    for sct_date in available_sct_dates:
        year=int(sct_date[0:4])
        month=int(sct_date[4:6])
        day=int(sct_date[6:])
        x=(year-year0)*12+(month-month0)+(day-day0)/31.0
        y=0.2
        x_list.append(x)
        y_list.append(y)

    fig=go.Figure ()
        
    fig.update_layout(
        # title="SCT timeline",
        paper_bgcolor='rgb(200,200,200)',
        height=100,
        width=700,
        margin=dict(
            l=2,
            r=2,
            b=2,
            t=2,
            pad=0
            ),
        hoverdistance=2,
        )

    fig.update_xaxes(
        visible=False,
        dtick=1,
        showgrid=False,
        range=[0.0,25.0],
        tickfont={'size':5,},
        # domain=[0.0,1.0],
        )

    fig.update_yaxes(
        visible=False,
        # domain=[0.0,1.0],
        range=[-1.5,0.7],
        )

    selected_color    ='#005eb8'
    not_selected_color='White'
    color_list=[]
    for i_date, flag in enumerate(selected_flags):
        if flag:
            color_list.append(selected_color)
        else:
            color_list.append(not_selected_color)

    marker=dict(color=color_list, size=18, line=dict(color='#005eb8', width=2))

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

    year_annotations=[]
    month_annotations=[]
    ann_x=[]
    ann_y=[]
    months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    years={2022:"'22", 2023:"'23", 2024:"'24"}
    for x in range(0,23):
        year=year0+int((month0+x)/12.0)
        month_label=months[(month0+x)%12]
        month_annotations.append("%s" % (month_label))
        year_annotations.append("%s" % (years[year]))
        ann_x.append(x+1.5)
        ann_y.append(-0.5)
    
    fig.add_trace(
        go.Scatter(
            mode='text',
            x=ann_x,
            y=ann_y,
            text=month_annotations,
            marker=marker,
            showlegend=False,
            hoverinfo="none",
        )
    )

    fig.add_trace(
        go.Scatter(
            mode='text',
            x=ann_x,
            y=[(yy-0.5) for yy in ann_y],
            text=year_annotations,
            marker=marker,
            showlegend=False,
            hoverinfo="none",
        )
    )

    for  x in range(1,24):
        fig.add_shape(type="rect",
            xref="x", yref="y",
            x0=x, y0=-1.2, x1=x+1, y1=-0.2,
            line=dict(
                color="#005eb8",
                width=0.2,
            ),
        )



    fig.layout.template=None

    data_json=json.dumps(fig.to_dict()['data'])
    layout_json=json.dumps(fig.to_dict()['layout'])

    timeline_info_json=json.dumps(available_sct_dates)

    return data_json, layout_json, timeline_info_json


