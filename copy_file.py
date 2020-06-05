
import numpy as np
import argparse
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument('-jobid', action='store', dest='jobid', type=int,
					help='jobid')
parser.add_argument('-fileloc', action='store', dest='fileloc', type=str,
					help='fileloc')
results = parser.parse_args()
jobid = int(results.jobid)
fileloc = results.fileloc

files = glob.glob('%s'%fileloc)

print(np.shape(files))

file = files[jobid]

command = 'cp %s muons.root'%file

os.system(command)
