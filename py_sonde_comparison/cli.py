from pywoudc import WoudcClient
from datetime import datetime, timedelta
from matplotlib.pyplot import *
import math
from pathlib import Path
import xarray as xr
import numpy as np
from scipy import interpolate
import os,sys,fnmatch
import seaborn as sns
import warnings
import click
warnings.filterwarnings("error", category=RuntimeWarning)
sns.set_theme(style="darkgrid")

from .logger import logger

# Note when running in environment, need to install pip install xarray[complete], need to find out why

'''
Python tool designed to allow for generic comparisons between WOUDC ozonesondes and multiple different satellite types.

Author: E Malina NASA/JPL/Caltech October 2022.

This program makes use of the WOUDC pywoudc package (https://github.com/woudc/pywoudc), to allow for easy pythonic access to the WOUDC datasets.
The author makes no claim to have written perfect or efficent code, if a more efficent method is apparent to a user, please discuss with the author
or current custodian before making changes. Or propose changes through github.
'''

def grab_woudc(start_date,end_date,gaw_locations): 
    # Function based on pywoudc information, grabs ozonesonde profiles
    # based on the supplied daterange

    # Invoke pyWoudc 
    client = WoudcClient()

    # Set date range for ozonesonde comparison
    begin = start_date
    end = end_date
    
    
    # Grab ozonesonde data, either all available data, or from a specific site
    if gaw_locations=='all':
        data = client.get_data('ozonesonde',
                                temporal=[begin, end])
    else:
        data = client.get_data('ozonesonde',
                            filters={'gaw_id': gaw_locations},
                            temporal=[begin, end])
        
    # Routine to check if any sonde data has been found by input specifications, if not
    # program exits.
    try:
        logger.info(f"Number of Sondes in date range {len(data['features'])}")
    except Exception as e:
        logger.error(f"No Sonde data available, or incorrect sonde site input, exiting.....{e}")   
        sys.exit(1)
    
    return data
    
def distance(lat1, long1, lat2, long2):
    
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    try:
        lat1, long1, lat2, long2 = map(math.radians, [lat1, long1, lat2, long2])
        # haversine formula 
        dlon = long2 - long1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        # Radius of earth in kilometers is 6371
        km = 6371* c
    except Exception as e:
        logger.error(f"Error in calculating colocation distance {e}")   
        sys.exit(1)
    return km

def convert_sensitivity(AK,apriori,model,AK_Log=True):
    
    # Short script to account for sensitivity between model and retrieval,
    # H(·) = xa + A(M(·) − xa), as Equation 7 in https://doi.org/10.5194/egusphere-2022-774
    
    # If Averaging Kernel is provided as log, currently assume this to be the case as standard.
    # Author notes, will likely need this section to be more flexible.
    try:
        if AK_Log == True:
            modified_profile = np.exp(np.log(apriori) + (AK@(np.log(model) - np.log(apriori))))
        elif AK_Log == False:
            modified_profile = apriori + (AK@(model - apriori))
        else:
            logger.error(f"Currently only True or False is accepted")   
            sys.exit(1)
    except RuntimeWarning as e:
        logger.warning(f"Warning in sensitivity modification :{e}")
        if AK_Log == True:
            modified_profile = np.exp(np.log(apriori) + (AK@(np.log(model) - np.log(apriori))))
        elif AK_Log == False:
            modified_profile = apriori + (AK@(model - apriori))
        else:
            logger.error(f"Currently only True or False is accepted")   
            sys.exit(1)
          
    except Exception as e:
        logger.error(f"Error in sensitivity modification :{e}")   
        sys.exit(1)

    
    return modified_profile

def convert_ppm_to_du(pressure,vmr):
    
    # This subroutine converts a profile of ozone values in ppm
    # into a single column value expressed as DU. Works between any particular pressure range.

    try:
        outO3 = []
        pressure_mid_total = []
        # First calculate mid points
        for i in range(len(pressure)-1):
            pressure_mid = (pressure[i+1] + pressure[i])/2
            pressure_mid_total.append(pressure_mid)

        # Then Calculate O3 VMRs at midpoint
        o3_mid = np.interp(np.flip(np.asarray(pressure_mid_total)),np.flip(pressure),np.flip(vmr))
        # Then calculate O3 DUs
        o3_mid = np.flip(o3_mid)
        for j in range(len(pressure)-1):
            o3DU = (float((o3_mid[j])/1000)*1e-6) * (((float(pressure[j])-float(pressure[j+1]))/9.8)*100*(1e-4)*(1/(28.96e-3))*(6.022e23)*(1/(2.6867e16)))
            outO3.append(o3DU)
    except Exception as e:
        logger.error(f"Error in calculating ozone column value: {e}")   
        sys.exit(1)

    return np.sum(outO3)

def read_product(path,dataset,start_date,end_date):
        
    # Read provided satellite data product, in order to provide standard data formats to the rest of the program.
    # May have to be modified to account for different products, current accepted products:
    # TROPESS

    try:
        # Reading data from TROPESS products
        if dataset.lower() == 'tropess-cris' or dataset.lower() == 'tropess-airsomi':
            # Start lists for storing data
            quality = []
            date = []
            hour = []
            latitude = []
            longitude = []
            ozone = []
            ozone_apriori = []
            aver_ker = []
            pressure = []

            time_period = end_date - start_date
                
            for j in range(0,time_period.days):
                #self.date.append(dates[j])
                dates = start_date + timedelta(days=j)
                if dataset.lower() == 'tropess-cris':
                    path_to_target = Path(f'/tb/CrIS/results/CRIS/Release_1.17.0/Global_Survey_Grid_0.8_RS/Products/{dates.year:02}/{dates.month:02}/{dates.day:02}/batch-01/L2_Products_Lite/CRIS_L2-O3-0_{dates.year:02}_{dates.month:02}_{dates.day:02}_F01_1.17_Litev01_Day_Night.nc').expanduser()
                elif dataset.lower() == 'tropess-airsomi':
                    path_to_target = Path(f'/tb/AIRSOMI/Release_1.17.0/Global_Survey_Grid_0.7/Products/{dates.year:02}/{dates.month:02}/{dates.day:02}/L2_Products_Lite/AIRS_OMI_ATrain_L2-O3_{dates.year:02}_{dates.month:02}_{dates.day:02}_F01_1.17_Litev01.nc').expanduser()
                
                    
                try:
                    # Use XArray to open and store dataset
                    general = (xr.open_dataset(path_to_target.as_posix(),engine="h5netcdf"))
                except Exception as e:
                    logger.info(f"{dates.year:02}_{dates.month:02}_{dates.day:02} Not available, skipping....")
                    continue
                        
                # Capturing TROPESS data, according the format of the data product.
                quality     = np.where((general.Quality.values > 0))[0]
                for l,k in enumerate(quality):
                    indpp = np.where(general.Pressure.values[k] > -999.0)[0]
                    date.append(datetime.strptime(str(int(general.YYYYMMDD.values[k])),'%Y%m%d').date())
                    latitude.append(general.Latitude.values[k])
                    longitude.append(general.Longitude.values[k])
                    ozone.append(general.Species.values[k,indpp])
                    ozone_apriori.append(general.ConstraintVector.values[k,indpp])
                    aver_ker.append(general.AveragingKernel.values[k,26-len(indpp):,26-len(indpp):])
                    pressure.append(general.Pressure.values[k,indpp])
                    hour.append(general.UT_Hour[k])
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
        
    return date,latitude,longitude,ozone,ozone_apriori,aver_ker,pressure,hour
    

@click.group()
def cli():
    pass


@cli.command(help="Colocate ozonesondes with provided satellite input")
@click.option('--dataset', '-ds', required=True, type=click.Choice(['TROPESS-CRIS'], case_sensitive=False),help='Indicate the source of the data in use.')
@click.option("--start-date", "-sd", required=True, type=click.DateTime(formats=["%Y-%m-%d"]), help="yyyy-mm-dd string that represents the start date of the analysis.")
@click.option("--end-date", "-ed", required=True, type=click.DateTime(formats=["%Y-%m-%d"]), help="yyyy-mm-dd string that represents the end date of the analysis.")
@click.option("--input", "-i", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True), help="input directory. L2 satellite ozone data is stored here.")
@click.option("--output", "-o", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True), help="output directory. npz files will be saved here. ")
@click.option('--ozone-units', '-ou', required=True, type=click.Choice(['None', 'ppb', 'ppm'], case_sensitive=False),help="Indicate what units are used in the data product")
@click.option('--gaw-locations', '-gl', required=True, type=click.Choice(['all'], case_sensitive=False),help="Indicate whether to make comparisons with all sonde locations, or a specific site")
@click.option('--distance-location', '-dl', required=True, type=float,help="Indicate perfered distance colocation criteria between satellite sounding and ozonesonde")
@click.option('--distance-time', '-dt', required=True, type=float,help="Indicate perfered maximum period in time for colocation between satellite sounding and ozonesonde")
def colocate(dataset,start_date,end_date,input,output,ozone_units,gaw_locations,distance_location,distance_time):
    try:   
        # The following subroutine colocates ozonesonde data with satellite retrievals, based on the input data.
        # All colocated data is output in the form of .npz files, which can then be read by other routines to plot data
        # and be manipulated as desired. 

        dates,latitudes,longitudes,ozone_profiles,ozone_aprioris,aver_kers,pressure,hours = read_product(input,dataset,start_date,end_date)

        
        latitudes = np.asarray(latitudes,dtype=object)
        longitudes = np.asarray(longitudes,dtype=object)
        
        # We currently do not know what units ozone will be 
        if ozone_units == str(None):
            logger.info("Satellite ozone profile units not selected, converting to ppb")
            ozone_profiles = np.asarray(ozone_profiles,dtype=object)*1e9
            ozone_aprioris = np.asarray(ozone_aprioris,dtype=object)*1e9
        elif ozone_units == 'ppb':
            ozone_profiles = np.asarray(ozone_profiles,dtype=object)
            ozone_aprioris = np.asarray(ozone_aprioris,dtype=object)
        elif ozone_units == 'ppm':
            ozone_profiles = np.asarray(ozone_profiles,dtype=object)*1000
            ozone_aprioris = np.asarray(ozone_aprioris,dtype=object)*1000
        else:
            print("Unit choice not supported,'None', 'ppb', or 'ppm' are currently supported.")
            logger.error("Unit choice not supported,'None', 'ppb', or 'ppm' are currently supported.")
            sys.exit(1)
            
        pressure = np.asarray(pressure,dtype=object)
        averaging_kernel = aver_kers

        # Grabs the relevant sonde data
        sonde_data = grab_woudc(start_date,end_date,gaw_locations)
        # Common pressure grid to interpolate to, based on CAMS grid
        pressure_grid = np.asarray([10.0,20.0,30.0,50.0,70.0,100.0,150.0,200.0,250.0,300.0,400.0,500.0,600.0,700.0,800.0,850.0,900.0,925.0,950.0,1000.0],dtype=float)
        
        # Initialising lists to save data, assuming will add to this in the future.
        difference_profile_percent = []
        difference_profile_absolute = []
        difference_troposphere_percent = []
        difference_troposphere_absolute = []     
        latitude_colocation = []
        time_vector = []
        
        # Initially check if code has been run before, and load datafile if it already exists. compare sonde date with satellite data date
        if not os.path.exists(Path(f'{output}/{dataset}_sonde_colocation_{start_date.year}_{start_date.month}_{start_date.day}_{end_date.year}_{end_date.month}_{end_date.day}.npz')): 
                    
            for i in range(0,len(sonde_data['features'])):
                ozone_date = datetime.strptime(sonde_data['features'][i]['properties']['instance_datetime'], '%Y/%m/%d %H:%M:%S+00') 
                for j in range(0,len(latitudes)):
                    
                    # Check if dates match with satellite data days
                    if ozone_date.year == dates[j].year and ozone_date.month == dates[j].month and ozone_date.day == dates[j].day:
                        # Check if time difference is less than 3 hours
                        if np.absolute(float(ozone_date.hour) - float(hours[j])) < distance_time:
                            # Check if satellite retrieval is within the specified distance
                            if distance(latitudes[j], longitudes[j], sonde_data['features'][i]['geometry']['coordinates'][1], sonde_data['features'][i]['geometry']['coordinates'][0]) <= distance_location:
                                logger.info(f"Match, Lat/long {latitudes[j]}, {longitudes[j]}, {sonde_data['features'][i]['geometry']['coordinates'][1]}, {sonde_data['features'][i]['geometry']['coordinates'][0]}, {ozone_date.year}, {ozone_date.month}, {ozone_date.day}")
                                # Grab data, convert to satellite retrieval grid and account for sensitivity
                                captured_data = sonde_data['features'][i]['properties']['data_block'].split('\r\n')
                                sonde_vmr_mid = []
                                sonde_pressure_mid = []

                                # Some sonde locations have different data formats
                                if captured_data[0].split(",")[0] == 'Duration':
                                    startPoint = 1
                                else:
                                    startPoint = 0

                                # Flag to check if too many values are missing in the ozonesonde dataset
                                errorBreak = 0
                                for iCapture in range(1,len(captured_data)-1): 

                                    # Grab all pressure and ozone values from sonde data, and check if all values are available.
                                    # empty strings are checked for with 'float', if missing are skipped.
                                    try:
                                        sonde_vmr_mid.append(float(captured_data[iCapture].split(",")[startPoint+1]))
                                        sonde_pressure_mid.append(float(captured_data[iCapture].split(",")[startPoint]))
                                    except ValueError:
                                        errorBreak+=1
                                        if errorBreak == 5:
                                            logger.info("Ozonesonde missing too many values, skipping....")
                                            break

                                        continue

                                # select valid sonde levels and check pressure is correct way around
                                if sonde_pressure_mid[0] > sonde_pressure_mid[1]:
                                    sonde_pressure_mid = np.flip(np.asarray(sonde_pressure_mid,dtype=float))
                                    indpp_2 = np.where(sonde_pressure_mid > 0)[0] 
                                    sonde_vmr_partial = np.flip(np.asarray(sonde_vmr_mid,dtype=float))[indpp_2]
                                else:
                                    sonde_pressure_mid = np.asarray(sonde_pressure_mid,dtype=float)
                                    indpp_2 = np.where(np.asarray(sonde_pressure_mid,dtype=float) > 0)[0] 
                                    sonde_vmr_partial = np.asarray(sonde_vmr_mid,dtype=float)[indpp_2]

                                sonde_vmr = (sonde_vmr_partial/(sonde_pressure_mid[indpp_2]*100000))*1e9

                                # Interpolate sonde to satellite retrieval pressure grid

                                # Check that the satellite pressure is surface first
                                if pressure[j][0] > pressure[j][1]:
                                    sat_pressure = np.flip(pressure[j][:])
                                    sat_ozone_profile = np.flip(ozone_profiles[j][:])
                                    sat_ozone_profile_prior = np.flip(ozone_aprioris[j][:])
                                    sat_averaging_kernel = np.flipud(np.fliplr(averaging_kernel[j][:][:]))
                                else:
                                    sat_pressure = pressure[j][:]
                                    sat_ozone_profile = ozone_profiles[j][:]
                                    sat_ozone_profile_prior = ozone_aprioris[j][:]
                                    sat_averaging_kernel = averaging_kernel[j][:][:]


                                # Interpolate sondes and satellites to common grid
                                # Try except to catch and remove strange behaviour
                                try:
                                    interp_model_sonde = interpolate.interp1d(np.asarray(sonde_pressure_mid)[indpp_2], sonde_vmr,fill_value="extrapolate")
                                    sonde_profile_mod = interp_model_sonde(pressure_grid)

                                    interp_model_satellite = interpolate.interp1d(sat_pressure,sat_ozone_profile,fill_value="extrapolate")
                                    satellite_profile_mod = interp_model_satellite(pressure_grid)
                                    interp_model_satellite_prior = interpolate.interp1d(sat_pressure, sat_ozone_profile_prior,fill_value="extrapolate")
                                    satellite_profile_apriori_mod = interp_model_satellite_prior(pressure_grid)
                                    interp_model_satellite_ak = interpolate.interp2d(sat_pressure,sat_pressure, sat_averaging_kernel)
                                    satellite_profile_ak_mod = interp_model_satellite_ak(pressure_grid,pressure_grid)
                                    # Modify Sondes to sensitivity of instrument
                                    sond_profile_ak = convert_sensitivity(satellite_profile_ak_mod,satellite_profile_apriori_mod,sonde_profile_mod)

                                    # Store differences and ignore large differences                          
                                    if np.absolute(100 * ((satellite_profile_mod - sond_profile_ak) / sond_profile_ak))[-1] < 200:
                                        difference_profile_percent.append(100 * ((satellite_profile_mod - sond_profile_ak) / sond_profile_ak))
                                        difference_profile_absolute.append((satellite_profile_mod - sond_profile_ak)* 1e9)

                                        # Setting Troposphere requirements as to HEGIFTOM:
                                        # From ground to 150 hPa in the tropics (within 15° )
                                        # From ground to 200 hPa in the subtropics (15°-30°)
                                        # From ground to 300 hPa in the midlatitudes (30°-60°)
                                        # From ground to 400 hPa in the polar regions (> 60°)
                                        if latitudes[j] > -15.0 and latitudes[j] < 15.0:
                                            end = 11
                                        elif latitudes[j] > -30.0 and latitudes[j] <= -15.0 or latitudes[j] < 30.0 and latitudes[j] >= 15.0:
                                            end = 12
                                        elif latitudes[j] > -60.0 and latitudes[j] <= -30.0 or latitudes[j] < 60.0 and latitudes[j] >= 30.0:
                                            end = 14
                                        elif latitudes[j] < -60.0 and latitudes[j] > 60.0:
                                            end = 15


                                        difference_troposphere_percent.append(100 * convert_ppm_to_du(pressure_grid[end:],((satellite_profile_mod[end:] - sond_profile_ak[end:]) / sond_profile_ak[end:])))
                                        difference_troposphere_absolute.append(convert_ppm_to_du(pressure_grid[end:],(satellite_profile_mod[end:] - sond_profile_ak[end:])* 1e6))
                                        latitude_colocation.append(latitudes[j])
                                        time_vector.append(ozone_date)

                                    else:
                                        logger.info("Warning sonde/satellite difference over 200%, skipping....")
                                        continue
                                except RuntimeWarning as e:
                                    logger.info(f"Runtime error {e}")
                                    continue

                        else:
                            continue
        

            with open(Path(f'{output}/{dataset}_sonde_colocation_{start_date.year}_{start_date.month}_{start_date.day}_{end_date.year}_{end_date.month}_{end_date.day}.npz'), 'wb') as f:
                np.savez(f,difference_profile_percent=difference_profile_percent,difference_profile_absolute=difference_profile_absolute, difference_troposphere_percent=difference_troposphere_percent,difference_troposphere_absolute=difference_troposphere_absolute,latitude_colocation=latitude_colocation,time_vector=time_vector)
                f.close()

        else:
            # Co-location routine checks to see if comparisons already exist.
            logger.info(f"Previous colocation file {dataset}_sonde_colocation_{start_date.year}_{start_date.month}_{start_date.day}_{end_date.year}_{end_date.month}_{end_date.day}.npz found, skipping colocation.")
         

        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
        
        

@cli.command(help="Plot colocation results from ozonesonde/satellite colocation")
@click.option('--available-datasets', '-dl', required=True,type=str,help='Indicate the source of the data in use. Must pass datasets as comma seperated list')
@click.option("--input", "-i", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True), help="input directory. The directory storing the colocated npz files.")
@click.option("--output", "-o", required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True), help="output directory. The directory to save the generated figures. ")
def plot_results(available_datasets,input,output):
    
    # This subroutine plots column comparisons, based on co-locations in the 'colocate' subroutine.
    # The input comparison_list takes a list of the satellite colocations, based on the output of colocate,
    # and plots together these results. 
    
    # The values in the comparison list must equal the'self.identifier' value in the name of each of the colocated,
    # files, ensuring the script knows what files to use.
    
    # Initialise the Figure
    try:
        sns.set_theme()
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
        fig,ax = subplots(ncols=1,nrows=1,figsize=(20,10),dpi=200)

        
        '''
        Author's note: The exact required statistics have not yet been defined, so this section is still very open for development
        '''
        # Split the input available datasets, so each one can be checked against what has been stored by colocate.
        available_datasets = list(available_datasets.split(','))

        # Grab data from the Co-location sub-routine.
        for root, directs, filenames in os.walk(os.path.abspath(input), topdown=False):
            for i in available_datasets:
                for filename in fnmatch.filter(filenames, f"{i}*.npz"):
                    # At this time, it will plot all files that match, so if multiple sonde/satellite comparison
                    # files of the same type but different dates exist, they will all be plotted.
                    npzfile = np.load(Path(f'{input}/{filename}'),allow_pickle=True)
                    logger.info("Colocated file found, loading...")
                    difference_profile_percent = npzfile['difference_profile_percent']
                    difference_profile_absolute = npzfile['difference_profile_absolute']
                    difference_troposphere_percent = npzfile['difference_troposphere_percent']
                    difference_troposphere_absolute = npzfile['difference_troposphere_absolute']
                    latitude_colocation = npzfile['latitude_colocation']
                    time_vector = npzfile['time_vector']
                    ax.plot(time_vector, difference_troposphere_percent,label=i)

        ax.set_xlabel('Time')
        ax.set_ylabel('Percent Difference HEGIFTOM Column Definition')
        ax.legend()
        savefig(Path(f'{output}/Sonde_Satellite_Ozone_Column_Comparison.png',format='png',bbox_inches = "tight"))
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)



