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

pair_data = np.load(fileloc_pairs+'FULL_collected_pair_info.npy')

print(np.shape(pair_data))		

# [pair_weight, nmeas_i, nmeas_j, rchi2_i, rchi2_j, P_i, P_j, doca, fid, dist, xv, yv, zv, np.sqrt(HNLMom[0]**2+HNLMom[1]**2+HNLMom[2]**2),x_to_ip, y_to_ip]
