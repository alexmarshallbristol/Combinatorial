import glob
import numpy as np

list_of_files = glob.glob('/eos/experiment/ship/user/amarshal/muflux_root_1M/muflux_*.root')

list_of_files = [int(element[57:-5]) for element in list_of_files]

list_of_files = np.asarray(list_of_files)

print(list_of_files, np.shape(list_of_files))

np.save('list_of_file_ID',list_of_files)