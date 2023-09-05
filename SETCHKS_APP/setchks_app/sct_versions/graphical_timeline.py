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
    # sct_dates=['20230215','20230705','20230802']
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
        title="SCT timeline",
        # width=400,
        # height=200,
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
            # marker=dict(
            #     color='LightSkyBlue',
            #     size=50,
            #     line=dict(
            #         color='MediumPurple',
            #         width=2
            #     )
            # ),
            showlegend=False,            
        )
    )

    fig.layout.template=None

    logger.debug(fig.to_dict())

    # return(fig.to_json())
    data_json=json.dumps(fig.to_dict()['data'])
    layout_json=json.dumps(fig.to_dict()['layout'])
    logger.debug(data_json)
    logger.debug(layout_json)
    return data_json, layout_json
    return(fig.to_dict())

# var defaultPlotlyConfiguration = { modeBarButtonsToRemove: ['sendDataToCloud', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'lasso2d', 'select2d'], displaylogo: false, showTips: true };
#     // display the plot in divId HTML element
#     Plotly.newPlot(divId, plotData, plotLayout, defaultPlotlyConfiguration);
