import numpy as np
import os
import netCDF4
import pandas as pd
import subprocess
import re
import shutil
import matplotlib.pyplot as plt

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
    
    print(" - Run Real")
    process = subprocess.call("mpiexec -np 9 ./real.exe".split())
    print(f" - Run WRF ({params})")
    process = subprocess.call(f"mpiexec -np 9 ./wrf.exe".split())
    
    # Retrive Output Data and return
    return get_folder('.')

def get_folder(folder) -> dict:
    files = sorted(os.listdir(folder))
    
    SWDTOTS = []
    TIMES = []
    for file in files:
        path = os.path.join(folder, file)
        
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

# Source shouldn't change but you never know
def cache_data(name, source='.', overwrite=True):
    files = os.listdir(source)    
    os.mkdir(name)
    
    for file in files:       
        src_path = os.path.join(source, file) 
        dest_path = os.path.join(name, file)
        
        match = re.match(r"wrfout_d01_2009-05-(\d\d)_(\d\d)", file)
        if match != None:
            if os.path.exists(dest_path):
                if overwrite:
                    # Remove and allow the move to execute
                    os.remove(dest_path)
                else:
                    # Keep the old file and get rid of the current file for cleanliness
                    os.remove(src_path)
                    continue
            # We *could* just use os.rename but this will work across disks, which may actually matter because WSL is goofy
            shutil.move(os.path.join(source, file), os.path.join(name, file))

if __name__ == "__main__":
    qs50 = run_model({'qh':700, 'qhl':900, 'qs': 50})
    cache_data('qs50')
    
    qs100 = run_model({'qh':700, 'qhl':900, 'qs': 100})
    cache_data('qs100')
    
    gt = get_true_data()
    
    qs50_data = []
    qs100_data = []
    gt_data = []
    for t in sorted(qs50.keys()):
        qs50_data.append(qs50[t])
        qs100_data.append(qs100[t])
        gt_data.append(gt[t])
        
    plt.plot(qs50_data, label='qs = 50')
    plt.plot(qs100_data, label='qs = 100')
    plt.plot(gt_data, label='ground truth')
    plt.savefig('test_plot.png')
    plt.show()