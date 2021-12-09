from dash import dash_table
from dash.dash_table.Format import Format

def datatable_settings_multiindex(df, flatten_char = '_',cols=False,unit=False):
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
            col_id = flatten_char.join(i)
            if unit:
                i =(i[0].upper(),i[1] + ' (AU)')
            else:
                df[i]=df[i]*1.496e+8
                i = (i[0].upper(),i[1] + ' (km)')
            datatable_col_list.append(dict(name= i, id= col_id,type='numeric',format=Format(precision=2)))
            columns_list.append(col_id)
        #datatable_col_list.append()
        df.columns = columns_list
        #print(df[ordered_cols[:8]].head())
        
    if cols:
        datatable_data = df[cols].dropna(how='all').to_dict('records')
        datatable_col_list=[d for d in datatable_col_list if d['id'] in cols]
    else:
        datatable_data = df[columns_list].dropna(how='all').to_dict('records')
        
    #print(type(datatable_data[0]['Date']),type(datatable_data[0]['solo_x']))

    return datatable_col_list, datatable_data
