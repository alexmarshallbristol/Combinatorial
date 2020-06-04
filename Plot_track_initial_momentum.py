
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

start_momentum = np.load('track_location_array_start_momentum.npy')

mom = np.sqrt(start_momentum[:,0]**2 + start_momentum[:,1]**2 + start_momentum[:,2]**2)
mom_t = np.sqrt(start_momentum[:,0]**2 + start_momentum[:,1]**2)

plt.hist2d(mom, mom_t, bins=75, norm=LogNorm())
plt.savefig('Initial_momentum')
