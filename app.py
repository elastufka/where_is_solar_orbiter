import dash
from dash import dash_table,dcc,html
from dash.dependencies import Input, Output #, State
import dash_bootstrap_components as dbc
#import dash_design_kit as ddk
import dash_daq as daq
import pygsheets

import plotly.graph_objects as go
import plotly.io as pio
#import plotly.colors
#import plotly.express as px

#from plotly.subplots import make_subplots

import pandas as pd
import numpy as np

from datetime import datetime as dt
from where_is_stix_utils import *
#from collections import Counter
#import base64

external_stylesheets = [dbc.themes.SOLAR] #lol
app = dash.Dash(__name__,external_stylesheets=external_stylesheets) #__name__,
server = app.server
app.title='Where is SOLO?'

# Figure styling
tt=pio.templates['plotly']
tt.layout.paper_bgcolor="#839496"
tt.layout.xaxis.showgrid=False
tt.layout.yaxis.showgrid=False
tt.layout.margin=dict(t=20,b=40)

imstyle={'min-height':500} #starting height of image element

#Tab styling
tabs_styles = {
    'height': '50px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'backgroundColor':'rgb(7, 54, 66)',
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'rgb(131, 148, 150)',
    'color': 'white',
    'padding': '10px'
}

#Data
spacecrafts=['SOLO','PSP','STEREO-A','BEPI']
bodies=['Mars','Venus']
cdict={'solo':'darkgoldenrod','psp':'blue','stereo-a':'magenta','bepi':'lightseagreen','mars':'firebrick','venus':'cyan'}

#df=pd.read_csv('data/trajectories.csv',header=[0,1])
#df.drop(columns=[('Unnamed: 0_level_0','Unnamed: 0_level_1')],inplace=True)
#df[('Date','-')]=pd.to_datetime(df.Date['-'])

gc = pygsheets.authorize(service_account_env_var = 'GDRIVE_API_CREDENTIALS')
aa=gc.open('trajectories')
df=aa[0].get_as_df(index_column=1)
first_row=df.iloc[0]
cols=pd.MultiIndex.from_arrays([np.array(df.keys()),np.array(first_row.values)])
df.drop('',inplace=True)
df.columns=cols
df[('Date','-')]=pd.to_datetime(df.Date['-'])
#new_tuples = df.index.map(lambda x: (x[0], pd.to_datetime(x[1])))
#df.index = pd.MultiIndex.from_tuples(new_tuples, names=["Date", "-"])
df2=df.copy(deep=True)
table_cols,table_data=datatable_settings_multiindex(df2)


########### layout

app.layout = html.Div([html.Div(children=dbc.Container([html.H1("Where is Solar Orbiter?", className="display-3"),
   html.P(
       "... and friends ",
       className="lead",
   ),
   #html.Hr(className="my-2"),
#   html.Div([
#        html.Div(html.P(children=[
#        "by ", html.A("Erica Lastufka",href="https://github.com/elastufka/")]),style={'width':'70%','display': 'inline-block','verticalAlign':'middle'}),
#    ])

    ],fluid=True, className="py-3",style={'background-image': 'url("/assets/so.png")','background-size':'35%','background-repeat':'no-repeat','background-position':'bottom right','margin-bottom':'0px','margin-top':'40px'}),className="p-3  rounded-3"),
    dcc.Tabs([
    dcc.Tab(label='Orbit Tool',children=[
    html.Div([
        html.Div(
               dcc.DatePickerRange(
               id='date-picker-range',
               min_date_allowed=dt(2020, 2, 5),
               max_date_allowed=dt.today(),
               display_format='DD MMM Y',
               #initial_visible_month=dt(2020, 2, 5),
               start_date=dt.today().replace(day=1),
               end_date=dt.today()),
                style={'width': '30%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div([
                dcc.Dropdown(id='spacecraft',options=[{'label': i, 'value': i} for i in spacecrafts],value=spacecrafts,multi=True,placeholder='Spacecraft')],
                style={'width': '30%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div(
                dcc.Dropdown(id='celestial bodies',options=[{'label': i, 'value': i} for i in bodies],value=[],multi=True,placeholder='Planets'),
                      style={'width': '25%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div(html.P('3D',style={'text-align':'right'}),style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div([daq.BooleanSwitch(id='dim',on=True,color="#839496")],style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div(html.P('2D',style={'text-align':'left'}),style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
                ]),
        html.Div(dcc.Graph(id='orbit'),style=imstyle),
    
    html.Div(children=[
    html.H2(dbc.Alert('Data Table',color='secondary'),style={'width': '89%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(html.P('km',style={'text-align':'right'}),style={'width': '3%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div([daq.BooleanSwitch(id='units',on=True,color="#839496")],style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(html.P('AU',style={'text-align':'left'}),style={'width': '3%', 'display': 'inline-block','verticalAlign':'middle'})
    ]),
    html.Div(
    dash_table.DataTable(id='tbl',data=table_data,columns=table_cols,
    page_size=20,
    style_cell={'textAlign': 'left'},
    style_as_list_view=True,
    style_header={
        'backgroundColor': 'rgb(131, 148, 150)',
        'color': 'white'},
    style_data={
        'backgroundColor': 'rgb(7, 54, 66)',
        'color': 'rgb(131, 148, 150)'},
    style_cell_conditional=[
        {'if': {'column_id': 'Date'},
         'width': '20%','fontWeight':'bold'}], export_format='csv'),style={'padding':'10px'}),
    html.Div(children=["Copyright 2021 ",html.A("Erica Lastufka",href="https://github.com/elastufka/")]),#]),
    ],style=tab_style,selected_style=tab_selected_style),#]),
    dcc.Tab(label='About',children=[
        html.Div(children=[html.P("This app gets spacecraft and celestial body data from the SPICE kernels.")],style={'padding': '1em'})],style=tab_style,selected_style=tab_selected_style)
    ],style=tabs_styles), #wish I could just include a html page...
        ])


@app.callback(
    [Output('orbit', 'figure'),Output('tbl','columns'),Output('tbl','data'),Output('date-picker-range','start_date'),Output('date-picker-range','end_date')],
    [Input('dim','on'),Input('spacecraft','value'),Input('celestial bodies','value'),Input('units','on'),Input('date-picker-range','start_date'),Input('date-picker-range','end_date')])
    
def update_orbit(dim,spacecraft,cbodies,unit,start_date,end_date):
    
    df0=df.where(df["Date"]["-"] >= start_date)
    dfc=df0.where(df0["Date"]["-"] <= end_date).dropna(how='all')
    ccols=['Date']
    
    skeys,bkeys=[],[]
    for s in spacecraft:
        skey=s.lower()
        skeys.append(skey)
        ccols.append(skey+'_x')
        ccols.append(skey+'_y')
        ccols.append(skey+'_z')
        
    for b in cbodies:
        bkey=b.lower()
        bkeys.append(bkey)
        ccols.append(bkey+'_x')
        ccols.append(bkey+'_y')
        ccols.append(bkey+'_z')
    
    fig=go.Figure()
    
    if not dim:
        hovertemp="x:%{x:.3f}, y:%{y:.3f}, z:%{z:.3f}<br>%{text}"
        xplane=np.linspace(-1,1,10)
        yplane=np.linspace(-1,1,10)
        xplane,yplane=np.meshgrid(xplane,yplane)
        
        xc=[np.cos(theta) for theta in np.linspace(0,2*np.pi,30)]
        yc=[np.sin(theta) for theta in np.linspace(0,2*np.pi,30)]
        single_color=[[0.0, 'rgb(200,200,200)'], [1.0, 'rgb(200,200,200)']]
        
        fig.add_trace(go.Surface(x=xplane,y=yplane,z=np.zeros(xplane.shape),showlegend=False,colorscale=single_color,showscale=False,opacity=0.5,hoverinfo='skip'))
        
        fig.add_trace(go.Scatter3d(x=xc,y=yc,z=np.zeros(len(xc)),mode='lines',line=dict(dash='dash',color='black'),showlegend=False,opacity=0.5,hoverinfo='skip'))
        fig.add_trace(go.Scatter3d(x=dfc.earth.y,y=dfc.earth.x,z=dfc.earth.z,name='Earth',mode='markers',marker=dict(color='green'),text=dfc.Date,hovertemplate=hovertemp))
        fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[0],name='Sun',mode='markers',marker=dict(color='orange',size=15))) #Heliocentric, sun at (0,0,0)
        
        for s in skeys:
            fig.add_trace(go.Scatter3d(x=dfc[s].y,y=dfc[s].x,z=dfc[s].z,marker_size=1,line=dict(color=cdict[s],width=3),name=s.upper(),text=dfc.Date,hovertemplate=hovertemp))
            
        for b in bkeys:
            fig.add_trace(go.Scatter3d(x=dfc[b].y,y=dfc[b].x,z=dfc[b].z,marker_size=1,line=dict(color=cdict[b]),name=b.capitalize(),hovertext=dfc.Date))
        
        #fig.update_traces(projection_z=dict(show=True))
        camera = dict(eye=dict(x=0, y=0.5, z=1.5))
        fig.update_layout(scene=dict(xaxis_title='HEE_y (AU)',yaxis_title='HEE_x (AU)',zaxis=dict(title='HEE_z (AU)',range=[-.25,.25]),camera=camera),height=500)
        
    else:
        hovertemp="x:%{x:.3f}, y:%{y:.3f}<br>%{text}"
        fig.add_shape(type="circle",
            xref="x", yref="y",
            x0=-1, y0=-1, x1=1, y1=1,
            fillcolor='rgb(200,200,200)',
            line_color='rgb(200,200,200)',
            opacity=.5)
        fig.add_trace(go.Scatter(x=dfc.earth.y,y=dfc.earth.x,name='Earth',mode='markers',marker=dict(color='green',symbol='circle-cross',line_color='black',line_width=1,size=8),text=dfc.Date,hovertemplate=hovertemp))
        fig.add_trace(go.Scatter(x=[0],y=[0],name='Sun',mode='markers',marker=dict(color='orange',size=15,symbol='circle-dot',line_color='black',line_width=2))) #Heliocentric, sun at (0,0,0)
        
        for s in skeys:
            fig.add_trace(go.Scatter(x=dfc[s].y,y=dfc[s].x,line=dict(color=cdict[s],width=4),name=s.upper(),text=dfc.Date,hovertemplate=hovertemp))
            
        for b in bkeys:
            fig.add_trace(go.Scatter(x=dfc[b].y,y=dfc[b].x,line=dict(color=cdict[b]),name=b.capitalize(),text=dfc.Date,hovertemplate=hovertemp))
        
        #fig.update_traces(projection_z=dict(show=True))
        fig.update_yaxes(scaleanchor='x',scaleratio=1)
        if 'mars' in bkeys:
            fig.update_yaxes(range=[2,-2])
        else:
            fig.update_yaxes(range=[1.1,-1.1])
        fig.update_layout(xaxis_title='HEE_y (AU)',yaxis_title='HEE_x (AU)',height=500)
        
    newcols,new_data=datatable_settings_multiindex(dfc,cols=ccols,unit=unit)
    
    return fig,newcols,new_data,start_date,end_date
        

if __name__ == '__main__':
    app.run_server(debug=True)
