import glob
import numpy as np

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

list_of_files = glob.glob('/eos/experiment/ship/user/amarshal/muflux_root_1M/muflux_*.root')

list_of_files = [int(find_between_r(element, "_", ".root" )) for element in list_of_files]

list_of_files = np.asarray(list_of_files)

print(list_of_files, np.shape(list_of_files))
np.save('list_of_file_ID',list_of_files)