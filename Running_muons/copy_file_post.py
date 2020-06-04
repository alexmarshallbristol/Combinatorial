
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-jobid', action='store', dest='jobid', type=int,
					help='jobid')
results = parser.parse_args()
jobid = int(results.jobid)

command = 'cp ship.conical.MuonBack-TGeant4_rec.root /eos/experiment/ship/user/amarshal/muflux_root_1M/ship.conical.MuonBack-TGeant4_rec_%s.root'%jobid

os.system(command)
