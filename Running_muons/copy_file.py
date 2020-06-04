
import numpy as np
import argparse
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument('-jobid', action='store', dest='jobid', type=int,
					help='jobid')
results = parser.parse_args()
jobid = int(results.jobid)

files = glob.glob('/eos/experiment/ship/user/amarshal/muflux_root_1M/muflux_*.root')

print(np.shape(files))

file = files[jobid]

command = 'cp %s muons.root'%file

os.system(command)
