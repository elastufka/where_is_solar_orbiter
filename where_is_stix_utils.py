from dash import dash_table
from dash.dash_table.Format import Format
import numpy as np

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
