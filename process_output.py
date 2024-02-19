import netCDF4
import numpy as np
import os
import re
# Takes data from outfolder, filters out non evaluated times, extracts SWDOWN ~ obs_swdtot, returns SWDOWN and saves
def process(wrffolder,epoch_name):
    def get_time_from_filename(filename):
        m = re.match(r"wrfout_d01_2009-05-(\d\d)_(\d\d):(\d\d):(\d\d)", filename)
        return (int(m[1]) - 6) * 24 + int(m[2]) + int(m[3]) / 60 + int(m[4]) / 3600

    files = [file for file in os.listdir(wrffolder) if file.startswith("wrfout")]
    data = []
    for outfile in files:
        nc = netCDF4.Dataset(os.path.join(wrffolder, outfile))
        data.append([get_time_from_filename(outfile), np.mean(nc["SWDOWN"][0, :]), np.mean(nc["SWDDIR"][0, :]), np.mean(nc["SWDDIF"][0,:]), np.mean(nc["SWDDIR"][0, :]) + np.mean(nc["SWDDIF"][0,:])])
    data = np.array(sorted(data, key=lambda x: x[0]))
    data = data[(data[:, 0] >= 12) & (data[:, 0] <= 27)]
    np.save(epoch_name + '.npy', data)
    return data