import numpy as np
import process_output
import os
import subprocess
import shutil
#from dotenv import load_dotenv
#load_dotenv()

# Functions to directly interface with the WRF-Solar Model

def update_params(params, PATH):    
    if 'beta_con' in params:
        params['beta_con'] = "{:.5E}".format(params['beta_con']).replace("E+", "E")
    with open('template.input', 'r') as reader:
        with open(f'{PATH}/namelist.input', 'w') as writer:
            writer.write(reader.read().format(**params))    

def run_WRF(PATH, max_tries, num_cores = 4):
    print(" - Run Real")
    subprocess.call(f"mpiexec -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
    print(" - Run WRF")
    for _ in range(max_tries):
        process = subprocess.call(f"mpiexec -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)
        if process == 0:
            return 1
    print(f"FAILED TO RUN IN {max_tries} ATTEMPTS")
    return 0


# Runs the model with given parameters and returns output as numpy arrays
def run_model(params: dict) -> np.array:
    epoch_name = "WRF" + "-".join([str(x) for x in params.values()])
    
    if epoch_name + '.npy' in os.listdir('cached_runs'):
        return np.load(os.path.join('cached_runs', epoch_name+'.npy'))
    PATH = "/home/capstoneii/Build_WRF/WRF/run"
    update_params(params, PATH)
    print(f"{params}")
    
    if not run_WRF(PATH, 10):
        exit()
    
    # Retrive Output Data and return
    data = process_output.process(PATH, epoch_name)
    cache_data(epoch_name + '.npy')
    return data

def cache_data(name):
    shutil.copy(name, 'cached_runs')