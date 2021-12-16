import numpy as np
import pandas as pd
import pygsheets
import heliopy.data.spice as spicedata
import heliopy.spice as hespice
from astropy import units as u
import glob
from astropy.time import Time
#from stix_utils import *
#from spacecraft_utils import *
#from visible_from_earth import coordinates_body
#from rotate_maps import coordinates_EARTH
from sunpy.coordinates.frames import HeliocentricEarthEcliptic
import spiceypy
from datetime import datetime as dt
from datetime import timedelta as td
import os

########## functions from libraries that are not loaded when this script is run in crontab (python_setup.py must not be run when this is the case) ############

def coordinates_SOLO(date_solo,light_time=False):
    """
    Load the kernel needed in order to derive the
    coordinates of Solar Orbiter and then return them in
    Heliocentric Earth Ecliptic (HEE) coordinates.
    """

    # Observing time (to get the SOLO coordinates)
    et_solo = spiceypy.datetime2et(date_solo)

    # Obtain the coordinates of Solar Orbiter
    solo_hee_spice, lighttimes = spiceypy.spkpos('SOLO', et_solo, 'SOLO_HEE_NASA', 'NONE', 'SUN')
    solo_hee_spice = solo_hee_spice * u.km

    # Convert the coordinates to HEE
    solo_hee = HeliocentricEarthEcliptic(solo_hee_spice,
                                         obstime=Time(date_solo).isot,
                                         representation_type='cartesian')

    if not light_time:
        # Return the HEE coordinates of Solar Orbiter
        return solo_hee
    else:
        return solo_hee,lighttimes

def coordinates_body(date_body,body_name,light_time=False):
    """
    Load the kernel needed in order to derive the
    coordinates of the given celestial body and then return them in
    Heliocentric Earth Ecliptic (HEE) coordinates.
    """

    # Observing time
    obstime = spiceypy.datetime2et(date_body)

    # Obtain the coordinates of Solar Orbiter
    hee_spice, lighttimes = spiceypy.spkpos(body_name, obstime,
                                     'SOLO_HEE_NASA', #  Reference frame of the output position vector of the object
                                     'NONE', 'SUN')
    hee_spice = hee_spice * u.km

    # Convert the coordinates to HEE
    body_hee = HeliocentricEarthEcliptic(hee_spice,
                                          obstime=Time(date_body).isot,
                                          representation_type='cartesian')
    if not light_time:
        # Return the HEE coordinates of the body
        return body_hee
    else:
        return body_hee,lighttimes
        
        
def locations_over_time(start_date,end_date,fn=coordinates_SOLO,body=None,output_unit=u.AU):
    '''return HEE locations of SOLO or a given celestial body over given time period'''
    date_range=pd.date_range(start_date,end_date)
    hee=[]
    for d in date_range:
        if body:
            hee.append(coordinates_body(d,body))
        else:
            hee.append(fn(d))
        
    xkm,ykm,zkm=[],[],[] #lists are fine for now
    for h in hee:
        xkm.append(h.x.to(output_unit).value)
        ykm.append(h.y.to(output_unit).value)
        zkm.append(h.z.to(output_unit).value)
    return date_range,xkm,ykm,zkm
    
def load_SOLO_SPICE(obs_date, path_kernel=os.environ['SPICE']):
    """
    Load the SPICE kernel that will be used to get the
    coordinates of the different spacecrafts.
    """
    #get cwd
    cwd=os.getcwd()

    # Convert string format to datetime
    obs_date = dt.strptime(obs_date, '%Y-%m-%dT%H:%M:%S')

    # Check if path_kernel has folder format
    if path_kernel[-1] != '/':
        path_kernel = path_kernel+'/'

    # Find the MK generation date ...
    MK_date_str = glob.glob(path_kernel+'/solo_*flown-mk_v*.tm')
    # ... and convert it to datetime
    MK_date = dt.strptime(MK_date_str[0][-15:-7], '%Y%m%d')

    # Check which kernel has to be loaded: 'flown' or 'pred'
    if obs_date < MK_date:
        spice_kernel = 'solo_ANC_soc-flown-mk.tm'
    else:
        spice_kernel = 'solo_ANC_soc-pred-mk.tm'
        print()
        print('**********************************************')
        print('The location of Solar Orbiter is a prediction!')
        print('Did you download the most recent SPICE kernel?')
        print('**********************************************')
        print()

    # Change the CWD to the given path. Necessary to load correctly all kernels
    os.chdir(path_kernel)

    # Load one (or more) SPICE kernel into the program
    spiceypy.spiceypy.furnsh(spice_kernel)

    print()
    print('SPICE kernels loaded correctly')
    print()

    #change back to original working directory
    os.chdir(cwd)
    
def furnish_kernels(spacecraft_list=['psp','stereo_a','stereo_a_pred','bepi_pred','psp_pred'],path_kernel=os.environ['SPICE']):
    k= spicedata.get_kernel(spacecraft_list[0])
    for sc in spacecraft_list[1:]:
        k+=spicedata.get_kernel(sc)
    cwd=os.getcwd()
    os.chdir(path_kernel)
    hespice.furnish(k)
    os.chdir(cwd)
    
def get_spacecraft_position(start_date,end_date,spacecraft='SPP', path_kernel=os.environ['SPICE']):
    ''' Use heliopy's Trajectory module to get position data through heliopy's SPICE wrapper
    
        Note: Have to be in the kernel directory while calling generate_positions... this is a pretty annoying thing about spiceypy'''
    times=pd.date_range(start_date,end_date)
    cwd=os.getcwd()
    sc = hespice.Trajectory(spacecraft)
    os.chdir(path_kernel)
    sc.generate_positions(times, 'Sun', 'HEE') 
    os.chdir(cwd)
    sc.change_units(u.au)
    return times,sc.x.value,sc.y.value,sc.z.value
    
    
############ now what is actually needed to update the trajectories ############

def load_kernels(today_str,path_kernel=os.environ['SPICE']):
    '''load all the SPICE kernels from their various locations and sources '''
    load_SOLO_SPICE(today_str,path_kernel=path_kernel)
    furnish_kernels(path_kernel=path_kernel)
    
def get_new_records(prev_record,today,last_row,path_kernel=os.environ['SPICE']):
    '''Get latest position data for spacecraft and planets, return as multiindex dataframe
    
    To be certain spiceypy can find everything it needs, run in the kernel directory'''
    cwd=os.getcwd()
    os.chdir(path_kernel)
    solo_hee=locations_over_time(prev_record,today)
    earth_hee=locations_over_time(prev_record,today,fn=coordinates_body,body='EARTH')
    mars_hee=locations_over_time(prev_record,today,fn=coordinates_body,body='MARS')
    venus_hee=locations_over_time(prev_record,today,fn=coordinates_body,body='VENUS')
    stereo_hee=get_spacecraft_position(prev_record,today,spacecraft='STEREO AHEAD',path_kernel=path_kernel)
    psp_hee=get_spacecraft_position(prev_record,today,path_kernel=path_kernel)
    bepi_hee=get_spacecraft_position(prev_record,today,spacecraft='MPO',path_kernel=path_kernel)
    os.chdir(cwd)
    
    sc=['solo','psp','stereo-a','bepi','earth','mars','venus']
    c=['x','y','z']
    scs,cc=['Date'],['-']
    
    for s in sc:
        for i in range(3):
            scs.append(s)
            cc.append(c[i])
    arrays=[np.array(scs),np.array(cc)]
    carr=[solo_hee[0],solo_hee[1],solo_hee[2],solo_hee[3],psp_hee[1],psp_hee[2],psp_hee[3],
    stereo_hee[1],stereo_hee[2],stereo_hee[3],bepi_hee[1],bepi_hee[2],bepi_hee[3],
    earth_hee[1],earth_hee[2],earth_hee[3],mars_hee[1],mars_hee[2],mars_hee[3],
    venus_hee[1],venus_hee[2],venus_hee[3]]
    dfm=pd.DataFrame(carr,index=arrays)
    dft=dfm.T
    dft.index = np.arange(last_row-2,last_row-3+len(dft)+1,1).tolist()
    return dft

def setup():
    '''Read Google sheet, get last row and last date updated, etc '''
    today=dt.now()
    today_str=dt.strftime(today,"%Y-%m-%dT%H:%M:%S")
    gc = pygsheets.authorize(service_file='/Users/wheatley/Documents/Solar/STIX/code/where-is-solar-orbiter-da3fe33c24a8.json') #(service_account_env_var = 'GOOGLE_CREDENTIALS') #environment variables not available to crontab! without some additional scripts run, so use full paths for now
    aa=gc.open('trajectories')
    df=aa[0].get_as_df()
    prev_record=pd.to_datetime(df['Date'].iloc[-1]) + td(days=1)
    last_row=df.iloc[-1][''] + 3
    return today,today_str,prev_record,last_row,aa[0]
    
def write_gsheet(worksheet,last_row,dft):
    '''write latest information to Google sheet'''
    for i,row in dft.iterrows():
        values=[i]
        for v in row.values.tolist():
            values.append(v)
        values[1]=str(values[1])
        print(values)
        worksheet.insert_rows(i+2, values= values,inherit=True)
    
if __name__ == "__main__":
    today,today_str,prev_record,last_row,worksheet=setup()
    path_kernel='/Users/wheatley/Documents/Solar/STIX/solar-orbiter/kernels/mk/' #os.environ['SPICE'] #environment variables not available to crontab!
    load_kernels(today_str,path_kernel=path_kernel)
    dft=get_new_records(prev_record,today, last_row,path_kernel=path_kernel)
    write_gsheet(worksheet,last_row,dft)
    print(f"Trajectories for {dft[('Date','-')]} successfully written!")
    

