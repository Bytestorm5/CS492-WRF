import numpy as np
import os
import netCDF4
import pandas as pd

# Functions to directly interface with the WRF-Solar Model
# Abstracting like this makes it easier to test

# get_true_data() and run_model() should output data in the same format/shape

# Gets the ground truth output data for the model as a numpy array
def get_true_data() -> tuple[np.ndarray, np.ndarray]:
    df = netCDF4.Dataset("sgpradflux10long_area_mean.c2.20090506_1200UTC.nc")
    return df["obs_time"][:].values, df['obs_swdtot'][:].values

# Runs the model with given parameters and returns output as numpy arrays
def run_model(params) -> tuple[np.ndarray, np.ndarray]:
    # TODO: Run Model
    EXECUTABLE_PATH = ""
    
    # Retrive Output Data
    OUT_DATA_PATH = ""
    files = sorted(os.listdir(OUT_DATA_PATH))
    
    SWDTOTS = np.zeros(len(files))
    TIMES = np.zeros(len(files))
    for i, file in enumerate(files):
        df = netCDF4.Dataset(os.path.join(OUT_DATA_PATH, file))
        TIMES[i] = df["XTIME"][0]
        SWDTOTS[i] = df["SWDOWN"][0][:].mean().mean()
    
    return TIMES, SWDTOTS
    
print(get_true_data())