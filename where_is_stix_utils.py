from dash import dash_table
from dash.dash_table.Format import Format,Scheme
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_data():
    credentials, project = google.auth.default()
    spreadsheet_id = "1ci0EoYK69LiO3W83TDeTZtn8JIzDLtJd4dlCn7qsvJA"
    ranges = ['trajectories!B1:W','flares!B1:BG','fit!E1:J']

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        for i,range in enumerate(ranges):
            result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range).execute()
            values = result.get('values', [])
            df=process_df(pd.DataFrame(values),i)
            yield df

    except HttpError as err:
        print(err)
        
#def load_data_pygsheets():
#    gc = pygsheets.authorize(service_account_env_var = 'GOOGLE_CREDENTIALS')
#    aa=gc.open('trajectories')
#    try:
#        for i in range(3):
#            df=aa[i].get_as_df(index_column=1,include_tailing_empty=False)
#            df=process_df(df,i)
#            yield df
#
#    except Exception as err:
#        print(err)
    
def process_df(df,i):
    '''do the processing for various dataframes'''
    if i==0:
        first_row=df.iloc[0]
        second_row=df.iloc[1]
        cols=pd.MultiIndex.from_arrays([np.array(first_row.values),np.array(second_row.values)])
        df.columns=cols
        #drop header rows
        df.drop([0,1],inplace=True)
        df=df.apply(pd.to_numeric,errors='ignore')
        df[('Date','-')]=pd.to_datetime(df.Date['-'])

#    ### load flare data
    elif i==1:
        excl_cols=['LC0_BKG','_id','goes','peak_UTC','CFL_X_arcsec','CFL_Y_arcsec','total_signal_counts','total_counts','peak_counts','flare_id','GOES_flux','LC0_peak_counts_4sec','solo_r','peak_utc','date_obs','hpc_bbox','frm_identifier','fl_peaktempunit','fl_peakemunit','fl_peakflux','fl_peakfluxunit','fl_peakem','fl_peaktemp','obs_dataprepurl','gs_thumburl','x_px','y_px','rotated_x_px','rotated_y_px','visible_from_SOLO','start_unix','end_unix','STIX_AIA_timedelta','STIX_AIA_timedelta_abs','stereo_z','x_arcsec','y_arcsec','x_deg','y_deg']
        df.columns=df.iloc[0]
        df.drop([0],inplace=True)
        df.drop(columns=excl_cols,inplace=True)
        df.drop_duplicates(subset=['peak_utc_corrected','event_peaktime'],inplace=True) #just in case any ssw latest events/flare detective results overlap
        imlinks=[f"[image]({imurl})" if imurl != '' else '' for imurl in df.gs_imageurl]
        movlinks=[f"[movie]({imurl})" if imurl != '' else '' for imurl in df.movie_url]
        df['frm_name']=[n[:n.find('-')] if isinstance(n,str) else None for n in df.frm_name] #shorten it
        df['AIA image_links']=imlinks
        df['AIA movie_links']=movlinks
        df=df.apply(pd.to_numeric,errors='ignore')
        df['event_peaktime']=pd.to_datetime(df.event_peaktime).astype(str)
        df['peak_utc_corrected']=pd.to_datetime(df.peak_utc_corrected).astype(str) #for 0 padding of hour...
        df.drop(columns=['gs_imageurl','movie_url'],inplace=True)

    else:
        df.columns=df.iloc[0]
        df.drop([0],inplace=True)
        df=df.apply(pd.to_numeric,errors='ignore')
    return df #,table_cols,table_data,fdf,table_cols2,table_data2

def format_datatable(df, flatten_char = '_',cols=False,unit=False,sphere=False):
    '''Create multiindex dataframe (non-native to Dash), format data given desired units and coordinate system'''
    datatable_col_list = [{"name": ('Date','-'), "id": 'Date','type':'text'}]
    columns_list = ['Date']
    for i in df.columns[1:]:
        original_c=i[1]
        if sphere and i[1]=='x': #change to spherical, change column list also
            #have to skip next columns too..
            xx,yy,zz=df[i].astype(float),df[(i[0],'y')].astype(float),df[(i[0],'z')].astype(float) #for readability - also sqrt and arctan require floats
            
            df[i]= np.sqrt(xx**2+yy**2+zz**2)#r
            df[(i[0],'y')]=np.arctan2(zz,np.sqrt(xx**2+yy**2)) #theta
            df[(i[0],'z')]=np.arctan2(yy,zz) #phi
            i=(i[0],'r')
        elif sphere and i[1]=='y':
            i=(i[0],'lat')
        elif sphere and i[1]=='z':
            i=(i[0],'lon')
        col_id = flatten_char.join(i)
        if unit:
            i =(i[0].upper(),i[1] + ' (AU)')
        else: #eventually make elif unit == km
            df[(i[0],original_c)]=df[(i[0],original_c)]*1.496e+8
            i = (i[0].upper(),i[1] + ' (km)')
        #then else: covers where unit == Rsun but have to change unit from BooleanSwitch to dropdown or RadioItems
        datatable_col_list.append(dict(name= i, id= col_id,type='numeric',format=Format(precision=2)))
        columns_list.append(col_id)

    df.columns = columns_list
        
    if cols: #don't display unwanted data
        datatable_data = df[cols].dropna(how='all').to_dict('records')
        datatable_col_list=[d for d in datatable_col_list if d['id'] in cols]
    else:
        datatable_data = df[columns_list].dropna(how='all').to_dict('records')
        
    return datatable_col_list, datatable_data
    
def get_flaretable_columns(fdf):
    table_cols=[]
    excl_cols=['rotated_lon_deg','rotated_lat_deg']
    rename_dict={'duration':'STIX flare duration (s)','GOES_class':'SOLO GOES class', 'peak_utc_corrected':'SOLO event peak (UTC)', 'peak_counts_corrected':'STIX peak counts at 1AU',
        'hpc_x':'AIA x (arcsec)', 'hpc_y':'AIA y (arcsec)', 'fl_goescls':'AIA GOES class',
        'rsun_apparent':'SOLO Rsun (arcsec)', 'rotated_x_arcsec':'SOLO x (arcsec)', 'rotated_y_arcsec':'SOLO y (arcsec)','stereo_x':'STEREO-A x (arcsec)', 'stereo_y':'STEREO-A y (arcsec)',
        'stereo_rsun_apparent':'STEREO-A Rsun (arcsec)','event_peaktime':'AIA event peak (UTC)','frm_name':'AIA flare dectection source','goes_proxy':'STIX GOES proxy'}
    ordered_cols=['event_peaktime','peak_utc_corrected','hpc_x','hpc_y','rotated_x_arcsec','rotated_y_arcsec','rsun_apparent']
    try:
        foo=fdf['stereo_x']
        ordered_cols.extend(['stereo_x','stereo_y','stereo_rsun_apparent'])
    except KeyError:
        pass
    ordered_cols.extend(['GOES_class','fl_goescls','goes_proxy','peak_counts_corrected','duration','AIA image_links','AIA movie_links','frm_name'])
    for c in fdf[ordered_cols].columns:
        if c not in excl_cols:
            if 'links' in c:
                table_cols.append(dict(name=c[:c.find('_')],id=c,type='text',presentation='markdown',deletable=True))
            elif type(fdf[c].iloc[1]) == str:
                table_cols.append(dict(name=rename_dict[c], id= c,type='text',deletable=True,selectable=True))
            else:
                if 'arcsec' in rename_dict[c]:
                    precision=2
                else:
                    precision=0
                table_cols.append(dict(name= rename_dict[c], id=c,type='numeric',format=Format(precision=precision,scheme=Scheme.fixed),deletable=True,selectable=True))
            
    return table_cols

def locations_on_disk(df, spacecraft,cbodies,cdict={'Solar Orbiter POV':'darkgoldenrod','Earth POV':'green','STEREO A POV':'magenta','bepi':'lightseagreen','mars':'firebrick','venus':'cyan'},msize='counts'):
    ''' Plot cartesian flare locations on solar disk using Plotly. '''
    stitles=['Earth POV']
    lkeys=[('hpc_x','hpc_y')]
    if 'SOLO' in spacecraft:
        stitles.append('Solar Orbiter POV')
        lkeys.append(('rotated_lon_deg','rotated_lat_deg'))
    if 'STEREO-A' in spacecraft:
        stitles.append('STEREO A POV')
        lkeys.append(('stereo_x','stereo_y'))
    #if 'BEPI' in spacecraft:
    #    stitles.append('BepiColombo')
        
    #scale marker sizes...
    if msize == 'STIX counts':
        mscaled=np.log10(df.peak_counts_corrected)*5.
    elif msize == 'GOES flux':
        mscaled=np.log10([goes_class_to_flux(f) for f in df.fl_goescls])*-2.
    else:
        mscaled=np.log10(df.duration/60)*10. #minutes
    
    #same with cbodies
    shapes=[]
    rsun_dict={'Solar Orbiter POV':90,'Earth POV':967,'STEREO A POV':997} #stddev 4" for stereo
        
    fig=make_subplots(rows=1,cols=len(stitles),subplot_titles=stitles,horizontal_spacing=0.1)
    for i,(kx,ky) in enumerate(lkeys):
        rsun_arcsec=rsun_dict[stitles[i]]
        if stitles[i] == 'Solar Orbiter POV':
            axbounds=100
            xunit='lon (deg)'
            yunit='lat (deg)'
            SO=True
        else:
            axbounds=np.round(rsun_arcsec,-3)
            xunit='x (arcsec)'
            yunit='y (arcsec)'
            SO=False

        cdata=gen_customdata(df,SO=SO)
        htemp=get_htemp(SO=SO)
        shapes.append(dict(type="circle",
        xref=f"x{i+1}", yref=f"y{i+1}",
        x0=-rsun_arcsec, y0=-rsun_arcsec, x1=rsun_arcsec, y1=rsun_arcsec,
        line_color="LightSeaGreen"))
        fig.add_trace(go.Scatter(x=df[kx],y=df[ky],mode='markers',marker_size=mscaled,marker_color=cdict[stitles[i]],customdata=cdata,hovertemplate=htemp,text=df.peak_utc_corrected,showlegend=False,name=stitles[i]),row=1,col=i+1) #can update traces later

        fig.update_xaxes(range=[-1*axbounds,axbounds],showgrid=False,zeroline=False, title=f'HPC {xunit}',row=1,col=i+1)
        fig.update_yaxes(range=[-1*axbounds,axbounds],scaleanchor=f'x{i+1}',scaleratio=1,showgrid=False,title=f'HPC {yunit}', row=1,col=i+1)
    fig.update_layout(shapes=shapes)
    return fig

def gen_customdata(df,SO=False):
    if SO:
        return np.array([df.rotated_x_arcsec,df.rotated_y_arcsec,df.rsun_apparent,df.peak_counts_corrected.values,df.duration.values/60.,df.fl_goescls.values]).T
    else:
        return np.array([df.peak_counts_corrected.values,df.duration.values/60.,df.fl_goescls.values]).T

def get_htemp(SO=False):
    if SO:
        return 'x rotated:%{customdata[0]:.0f}", y rotated:%{customdata[1]:.0f}", Rsun:%{customdata[2]:.0f}"<br>%{text|%Y-%m-%d %H:%M:%S}<br>Peak Counts: %{customdata[3]:.0f}<br>Duration: %{customdata[4]:.1f} min<br>GOES class: %{customdata[5]}'
    return 'x:%{x:.0f}", y:%{y:.0f}"<br>%{text|%Y-%m-%d %H:%M:%S}<br>Peak Counts: %{customdata[0]:.0f}<br>Duration: %{customdata[1]:.1f} min<br>GOES class: %{customdata[2]}'
    
def goes_class_to_flux(class_in):
    gdict={'A':-8,'B':-7,'C':-6,'M':-5,'X':-4}
    if len(class_in) > 1:
        goes_flux=float(class_in[1:])*10**gdict[class_in[0]]
    elif class_in !='': #just the letter
        goes_flux=10**gdict[class_in[0]]
    else:
        goes_flux=10**-8.5#None #just for this app
    return goes_flux
    
def goes_flux_to_class(flux_in):
    gdict={-8:'A',-7:'B',-6:'C',-5:'M',-4:'X'}
    try:
        letter=gdict[np.floor(np.log10(flux_in))]
    except KeyError:
        if np.log10(flux_in) < -8:
            letter='A'
        elif np.log10(flux_in) > -4:
            letter='X'
    number=np.round(flux_in/(10**np.floor(np.log10(flux_in))),1)
    return letter+str(number)


def goes_proxy(fitdf,counts):
    return [goes_flux_to_class(10**(fitdf['slope'].iloc[-1]*np.log10(c)+fitdf['intercept'].iloc[-1])) if ~np.isnan(c) else None for c in counts.values]
