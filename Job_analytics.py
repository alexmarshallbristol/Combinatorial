import glob
import numpy as np
import ROOT
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-fileloc_rec', action='store', dest='fileloc_rec', type=str,
                                        help='fileloc_rec')
parser.add_argument('-fileloc_muons', action='store', dest='fileloc_muons', type=str,
                                        help='fileloc_muons')
parser.add_argument('-fileloc_pairs', action='store', dest='fileloc_pairs', type=str,
                                        help='fileloc_pairs')
parser.add_argument('-num_pairs', action='store', dest='num_pairs', type=int,
                                        help='num_pairs')
parser.add_argument('-num_cores', action='store', dest='num_cores', type=int,
                                        help='num_cores')
results = parser.parse_args()
fileloc_rec = results.fileloc_rec
fileloc_muons = results.fileloc_muons
fileloc_pairs = results.fileloc_pairs
num_pairs = results.num_pairs
num_cores = results.num_cores

# MUON_FILES="/eos/experiment/ship/user/amarshal/muflux_root_1M/muflux_*.root"

# REC_FILES="/eos/experiment/ship/user/amarshal/muflux_root_1M/"

# PAIR_DATA="/eos/experiment/ship/user/amarshal/muflux_root_1M/"


muon_files = glob.glob(fileloc_muons)

# print(muon_files)


def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

print(' Checking muon input files... ')
muon_file_id_list = np.empty(0)

for file in muon_files:

	# print(file)
	file_id = int(find_between_r(file,'_','.root'))
	# print(file_id)

	try:
		f = ROOT.TFile(file)
		# f.ls()
		sTree = f.Get("pythia8-Geant4")
		nEvents = sTree.GetEntries()-1 # -1 because GAN file appends an extra blank muon

		# print(nEvents)
		muon_file_id_list = np.append(muon_file_id_list, file_id)
	except:
		print(file_id, 'broken file')
	# break


print(' Checking FairShip reconstructed files... ')
rec_file_id_list = np.empty(0)

rec_files = glob.glob(fileloc_rec+'ship.conical.MuonBack-TGeant4_rec_*.root')

# print(muon_files)

for file in rec_files:

	# print(file)
	file_id = int(find_between_r(file,'_','.root'))
	# print(file_id)
	# quit()

	try:
		f = ROOT.TFile(file)
		# f.ls()
		sTree = f.Get("cbmsim")
		nEvents = sTree.GetEntries() # -1 because GAN file appends an extra blank muon

		print(nEvents)
		rec_file_id_list = np.append(rec_file_id_list, file_id)
	except:
		print(file_id,'broken file')
	# break


print(muon_file_id_list, np.shape(muon_file_id_list))
print(rec_file_id_list, np.shape(rec_file_id_list))

# number of pairs created, number of pairs wanted


