import dash
from dash import dash_table,dcc,html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

from datetime import datetime as dt
from where_is_stix_utils import *

######### setup

external_stylesheets = [dbc.themes.SOLAR] #lol
#meta_tags={'metas':}    html.Meta(property='og:image', content='/assets/screenshot.jpg') #so that this shows up when sharing
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server
app.title='Where is SOLO?'

########### Figure styling
tt=pio.templates['plotly']
tt.layout.paper_bgcolor="#839496"
tt.layout.xaxis.showgrid=False
tt.layout.yaxis.showgrid=False
tt.layout.margin=dict(t=20,b=40)

imstyle={'min-height':450} #starting height of image element

########## Tab styling
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

######## Data labels and colors
spacecrafts=['SOLO','PSP','STEREO-A','BEPI']
bodies=['Mars','Venus']
jvis=['Earth','SOLO','STEREO-A']#,'BEPI','Mars','Venus']
msizes=['STIX counts','GOES flux','STIX duration']
cdict={'solo':'darkgoldenrod','psp':'blue','stereo-a':'magenta','bepi':'lightseagreen','mars':'firebrick','venus':'cyan','earth':'green'}

####### Load the data

datagen = load_data()
#print('loaded from Sheets API')
df,fdf,fitdf=list(datagen)
df2=df.copy(deep=True)
table_cols,table_data=format_datatable(df2)
fdf['goes_proxy']=goes_proxy(fitdf,fdf.peak_counts_corrected)
table_cols2 = get_flaretable_columns(fdf)
table_data2 = fdf.to_dict('records')

page_size=20

########### About markdown
mdlines=open('about.md').readlines()

########### app layout

app.layout = html.Div([html.Div(children=dbc.Container([html.H1("Where is Solar Orbiter?", className="display-3"),
   html.P(
       "... and friends ",
       className="lead",
   )],fluid=True, className="py-3",style={'background-image': 'url("/assets/so.png")','background-size':'35%','background-repeat':'no-repeat','background-position':'bottom right','margin-bottom':'0px','margin-top':'40px'}),className="p-3 rounded-3"),
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
    html.H2(dbc.Alert('Coordinates',color='secondary'),style={'width': '70%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(html.P('km',style={'text-align':'right'}),style={'width': '3%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div([daq.BooleanSwitch(id='units',on=True,color="#839496")],style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(html.P('AU',style={'text-align':'left'}),style={'width': '3%', 'display': 'inline-block','verticalAlign':'middle'}), #do switch for cartesian or spherical also
    html.Div(html.P('Cartesian',style={'text-align':'right'}),style={'width': '7%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div([daq.BooleanSwitch(id='coord_type',on=False,color="#839496")],style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(html.P('Spherical',style={'text-align':'left'}),style={'width': '7%', 'display': 'inline-block','verticalAlign':'middle'})
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
    dcc.Tab(label='Solar Flares',id='flare_tab',value='flare',children=[
    html.Div([
    html.Div(children=[html.P("Show only jointly visible flares: "),dcc.Checklist(id='jointvis',
    options=[{'label': i, 'value': i} for i in jvis],
    value=['Earth', 'SOLO'],inputStyle={"margin-right": "5px"},
    labelStyle={'display': 'inline-block','padding-right':'.5em'})],style={'width': '50%', 'display': 'inline-block','verticalAlign':'middle'}),
    html.Div(children=[html.P("Marker sizing: "),dcc.RadioItems(id='msize',
    options=[{'label': i, 'value': i} for i in msizes],
    value='STIX counts',inputStyle={"margin-right": "5px"},labelStyle={'display': 'inline-block','padding-right':'.5em'})],style={'width': '50%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.Div(dcc.Graph(id='flares'),style=imstyle),
        
        html.Div(children=[
        html.H2(dbc.Alert('Flare Data',color='secondary'),style={'width': '60%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.P('results per page',style={'width': '10%', 'display': 'inline-block','verticalAlign':'middle','margin-left':'20px'}),
        dcc.Input(id='nresults',type='number',value=page_size,style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
        html.P('limit plot results',style={'text-align':'right','width': '10%', 'display': 'inline-block','verticalAlign':'middle'}),
        daq.BooleanSwitch(id='limit',on=True,color="#839496",style={'width': '5%', 'display': 'inline-block','verticalAlign':'middle'}),
        ]),
    html.Div(
    dash_table.DataTable(id='tbl2',data=table_data2,columns=table_cols2,
    page_size=page_size,
    sort_action="native",
    #sort_mode="multi",
    style_cell={'textAlign': 'left'},
    style_as_list_view=True,
    style_header={
        'backgroundColor': 'rgb(131, 148, 150)',
        'color': 'white','whiteSpace':'normal'},
    style_data={
        'backgroundColor': 'rgb(7, 54, 66)',
        'color': 'rgb(131, 148, 150)'},
    style_cell_conditional=[
        {'if': {'column_id': 'Date'},
         'width': '20%','fontWeight':'bold'}], export_format='csv'),style={'padding':'10px'}),
    html.Div(children=["Copyright 2021 ",html.A("Erica Lastufka",href="https://github.com/elastufka/")]),
    ])],style=tab_style, selected_style=tab_selected_style), #why does dash markdown not display tables in the .md file correctly?
    dcc.Tab(label='About',children=[
        html.Div(children=[dcc.Markdown('''
        # Trajectories
        
        ## Satellites
        
        | Full Name  | Abbreviation  |
        | :--- | :--- |
        | Solar Orbiter  | SOLO  |
        | Parker Solar Probe  | PSP  |
        |  Solar TErrestrial RElations Observatory (Ahead) | STEREO-A  |
        | BepiColombo | BEPI |
        
        &nbsp;
        
        ## Data Sources
        
        Ultimately, all orbit trajectory data is derived from the [SPICE](https://naif.jpl.nasa.gov/naif/data.html) kernels. It is accessed using various Python wrappers.
        
        | Orbiting body  | Kernel source  |
        | :--- | :--- |
        | SOLO  | [SOCCI](https://repos.cosmos.esa.int/socci/projects/SPICE_KERNELS/repos/solar-orbiter/browse/kernels/ck) updated weekly |
        | PSP  | [heliopy](https://docs.heliopy.org/en/0.5.3/spice.htmll) psp & psp-pred |
        | STEREO-A | [heliopy](https://docs.heliopy.org/en/0.5.3/spice.html) stereo-a |
        | BEPI | [heliopy](https://docs.heliopy.org/en/0.5.3/spice.html) bepi-pred |
        | Venus | [spiceypy](https://spiceypy.readthedocs.io/en/master/) |
        | Earth | [spiceypy](https://spiceypy.readthedocs.io/en/master/) |
        | Mars | [spiceypy](https://spiceypy.readthedocs.io/en/master/) |'''),dcc.Markdown(mdlines)],style={'padding': '1em'})],style=tab_style,selected_style=tab_selected_style)
        ]) ])


@app.callback(
    [Output('orbit', 'figure'),Output('tbl','columns'),Output('tbl','data'),Output('date-picker-range','start_date'),Output('date-picker-range','end_date')],
    [Input('dim','on'),Input('spacecraft','value'),Input('celestial bodies','value'),Input('units','on'),Input('coord_type','on'),Input('date-picker-range','start_date'),Input('date-picker-range','end_date')])
    
def update_orbit(dim,spacecraft,cbodies,unit,coord_type,start_date,end_date):
    
    df0=df.where(df["Date"]["-"] >= start_date)
    dfc=df0.where(df0["Date"]["-"] <= end_date).dropna(how='all')
    ccols=['Date']
    
    skeys,bkeys=[],[]
    
    if coord_type:
        k1,k2,k3='_r','_lat','_lon'
    else:
        k1,k2,k3='_x','_y','_z'
        
    for s in spacecraft:
        skey=s.lower()
        skeys.append(skey)
        for k in [k1,k2,k3]:
            ccols.append(skey+k)
        
    for b in cbodies:
        bkey=b.lower()
        bkeys.append(bkey)
        for k in [k1,k2,k3]:
            ccols.append(bkey+k)

    fig=go.Figure() #can animate this eventually...
    
    if not dim:
        hovertemp="x:%{y:.3f}, y:%{x:.3f}, z:%{z:.3f}<br>%{text}"
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
        hovertemp="x:%{y:.3f}, y:%{x:.3f}<br>%{text}"
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
        

        fig.update_yaxes(scaleanchor='x',scaleratio=1)
        if 'mars' in bkeys:
            fig.update_yaxes(range=[2,-2])
        else:
            fig.update_yaxes(range=[1.1,-1.1])
        fig.update_layout(xaxis_title='HEE_y (AU)',yaxis_title='HEE_x (AU)',height=500)
        
    newcols,new_data=format_datatable(dfc,cols=ccols,unit=unit,sphere=coord_type)
    
    return fig,newcols,new_data,start_date,end_date #need to return dates to element so it'll display the correct calendar month in DatePicker
        
@app.callback([Output('tbl2','columns'),Output('tbl2','data'),Output('tbl2','page_size')], [Input('tbl2','columns'),Input('spacecraft','value'),Input('celestial bodies','value'),Input('date-picker-range','start_date'),Input('date-picker-range','end_date'),Input('flare_tab', 'value'),Input('jointvis', 'value'),Input('nresults','value')])
def display_content(table_cols2,spacecraft, cbodies, start_date,end_date,selected_tab,jointvis,nresults):
    #print(jointvis) #use to filter flare selection...
    if selected_tab == 'flare':
        fdf0=fdf.where(fdf["peak_utc_corrected"] >= start_date)
        fdfc=fdf0.where(fdf0["peak_utc_corrected"] <= end_date).dropna(how='all')
        for vis in jointvis:
            if vis == 'Earth':
                fdfc=fdfc.where(~np.isnan(fdfc['hpc_x'])).dropna(how='all')
            if vis == 'SOLO':
                fdfc=fdfc.where(~np.isnan(fdfc['peak_counts_corrected'])).dropna(how='all')
                if 'Earth' in jointvis:
                    fdfc=fdfc.where(~np.isnan(fdfc['rotated_x_arcsec'])).dropna(how='all')
            if vis == 'STEREO-A':
                fdfc=fdfc.where(~np.isnan(fdfc['stereo_x'])).dropna(how='all')
        if 'STEREO-A' not in spacecraft: #remove these columns
            fdfc.drop(columns=['stereo_x','stereo_y','stereo_rsun_apparent'],inplace=True)
            table_cols2=get_flaretable_columns(fdfc)
        table_data2 = fdfc.to_dict('records')
        return table_cols2,table_data2,nresults
    return [],[]
    
@app.callback(Output('flares', 'figure'), [Input('flare_tab', 'value'),Input('tbl2','data'),Input('tbl2','sort_by'),Input('spacecraft','value'),Input('celestial bodies','value'),Input('msize', 'value'),Input('nresults','value'),Input('limit','on')])
def display_content(selected_tab,table_data,sortby,spacecraft, cbodies,msize,nresults,limit):
    '''take input for figure directly from data table, so any sorting is reflected '''
    if len(table_data) !=0:
        table_df=pd.DataFrame(table_data).sort_values('peak_utc_corrected')
        asc=True
        if not limit:
            if sortby is not None:
                if sortby[0]['direction']!='asc':
                    asc=False
                table_df=table_df.sort_values(sortby[0]['column_id'],ascending=asc)
            table_df=table_df.head(nresults)
        if selected_tab == 'flare':
            return locations_on_disk(table_df, spacecraft,cbodies,msize=msize)
    else:
        return {"layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                        "text": "No matching data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 28}
                    }]
            }}

if __name__ == '__main__':
    app.run_server(debug=True)
