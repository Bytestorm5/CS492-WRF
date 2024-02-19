import netCDF4
import numpy as np
import os
def get_GT():
  GTDIR = 'Ground_Truth'
  if 'ground_truth.npy' in os.listdir(GTDIR):
    return np.load('Ground_Truth/ground_truth.npy')
  pathToGT = os.path.join(GTDIR, 'sgpradflux10long_area_mean.c2.20090506_1200UTC.nc')
  GT = netCDF4.Dataset(pathToGT)
  npGT = np.array(GT['obs_swdtot'])
  np.save('Ground_Truth/ground_truth.npy', npGT, allow_pickle=True, fix_imports=True)
  return npGT