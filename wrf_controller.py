import numpy as np
import os
import netCDF4
import pandas as pd
import subprocess
import re

# Functions to directly interface with the WRF-Solar Model
# Abstracting like this makes it easier to test

# get_true_data() and run_model() should output data in the same format/shape

# Gets the ground truth output data for the model as a numpy array
def get_true_data() -> dict:
    df = netCDF4.Dataset("sgpradflux10long_area_mean.c2.20090506_1200UTC.nc")
    return {time: val for time, val in zip(np.array(df["obs_time"][:]), np.array(df['obs_swdtot'][:]))}

# Runs the model with given parameters and returns output as numpy arrays
def run_model(params: dict) -> dict:
    # Update namelist with template
    with open('template.input', 'r') as reader:
        with open('namelist.input', 'w') as writer:
            writer.write(reader.read().format(**params))
    
    process = subprocess.run("mpiexec -np 9 ./wrf.exe")
    if process.returncode != 0:
        print("--- ERROR IN WRF EXECUTION; ABORTING ---")
        exit()
    
    # Retrive Output Data
    OUT_DATA_PATH = "."
    files = sorted(os.listdir(OUT_DATA_PATH))
    
    SWDTOTS = []
    TIMES = []
    for file in files:
        path = os.path.join(OUT_DATA_PATH, file)
        
        match = re.match(r"wrfout_d01_2009-05-(\d\d)_(\d\d)", file)
        if match != None:   
            time = int(match.group(2)) if match.group(1) == '06' else int(match.group(2))+24 
            if time < 12 or time > 27:
                continue
            
            # This is stupid but netCDF doesn't play nice with the special characters
            os.rename(path, path[:-6])
            df = netCDF4.Dataset(path[:-6])                
            
            TIMES.append(time)
            SWDTOTS.append(df["SWDOWN"][0][:].mean().mean()) 
            df.close()
            os.rename(path[:-6], path)    
        
    return {time: val for time, val in zip(TIMES, SWDTOTS)}
