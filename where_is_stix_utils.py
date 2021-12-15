from dash import dash_table
from dash.dash_table.Format import Format
import numpy as np

def cart2sphere(xx,yy,zz):
    rr,llat,llon=[],[],[]
    for x,y,z in zip(xx,yy,zz):
        r = np.sqrt(x**2+ y**2 + z**2)            # r
        theta = np.arctan2(z,np.sqrt(x**2+ y**2))     # theta
        phi = np.arctan2(y,x)                        # phi
        #return r, theta, phi
        rr.append(r)
        llat.append(theta)
        llon.append(phi)
    return rr,llat,llon

def datatable_settings_multiindex(df, flatten_char = '_',cols=False,unit=False,sphere=False):
    ''' Plotly dash datatables do not natively handle multiindex dataframes. This function takes a multiindex column set
    and generates a flattend column name list for the dataframe, while also structuring the table dictionary to represent the
    columns in their original multi-level format.

    Function returns the variables datatable_col_list, datatable_data for the columns and data parameters of
    the dash_table.DataTable
    
    default units are AU'''
    datatable_col_list = [{"name": ('Date','-'), "id": 'Date','type':'text'}]
    levels = df.columns.nlevels
    if levels == 1:
        for i in df.columns[:-1]: #date is special
            datatable_col_list.append({"name": i, "id": i})
    else:
        columns_list = ['Date']
        for i in df.columns[1:]:
            original_c=i[1]
            if sphere and i[1]=='x': #change to spherical, change column list also
                #have to skip next columns too..
                r,lat,lon=cart2sphere(df[i].values,df[(i[0],'y')].values,df[(i[0],'z')].values)
                #print(len(r),len(df[i].values))
                df[i]=r
                df[(i[0],'y')]=lat
                df[(i[0],'z')]=lon
                i=(i[0],'r')
                #df.drop(columns=[(i[0],'y'),(i[0],'z')],inplace=True)
            elif sphere and i[1]=='y':
                i=(i[0],'lat')
            elif sphere and i[1]=='z':
                i=(i[0],'lon')
            col_id = flatten_char.join(i)
            if unit:
                i =(i[0].upper(),i[1] + ' (AU)')
            else:
                #print('here',i,df.columns)
                df[(i[0],original_c)]=df[(i[0],original_c)]*1.496e+8
                i = (i[0].upper(),i[1] + ' (km)')
            datatable_col_list.append(dict(name= i, id= col_id,type='numeric',format=Format(precision=2)))
            columns_list.append(col_id)

        df.columns = columns_list

        
    if cols:
        datatable_data = df[cols].dropna(how='all').to_dict('records')
        datatable_col_list=[d for d in datatable_col_list if d['id'] in cols]
    else:
        datatable_data = df[columns_list].dropna(how='all').to_dict('records')
        
    #print(type(datatable_data[0]['Date']),type(datatable_data[0]['solo_x']))

    return datatable_col_list, datatable_data
