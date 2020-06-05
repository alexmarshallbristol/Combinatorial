
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-jobid', action='store', dest='jobid', type=int,
					help='jobid')
parser.add_argument('-fileloc', action='store', dest='fileloc', type=str,
					help='fileloc')
results = parser.parse_args()
jobid = int(results.jobid)
fileloc = results.fileloc

command = 'cp ship.conical.MuonBack-TGeant4_rec.root %sship.conical.MuonBack-TGeant4_rec_%s.root'%(fileloc,jobid)

os.system(command)
