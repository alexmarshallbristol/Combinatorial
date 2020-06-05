import glob
import numpy as np
import ROOT
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-fileloc_pairs', action='store', dest='fileloc_pairs', type=str,
                                        help='fileloc_pairs')
results = parser.parse_args()
fileloc_pairs = results.fileloc_pairs

files = glob.glob(fileloc_pairs+'collected_pair_info_*')

FULL_collected_pair_info = np.empty((0,16))

for file in files:

	current = np.load(file)

	# print(np.shape(current))
	FULL_collected_pair_info = np.append(FULL_collected_pair_info, current, axis=0)
	print(np.shape(FULL_collected_pair_info))
	# quit()

np.save(fileloc_pairs+'FULL_collected_pair_info.npy', FULL_collected_pair_info)