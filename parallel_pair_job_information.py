import numpy as np
import math

track_location_array = np.load('track_location_array.npy')
print(np.shape(track_location_array))
num_tracks = np.shape(track_location_array)[0]

pairs_to_sample = int(2E6)

nx, ny = num_tracks, num_tracks
xy = np.mgrid[:nx,:ny].reshape(2, -1).T

print(np.shape(xy))

sample = xy.take(np.random.choice(xy.shape[0], pairs_to_sample, replace=False), axis=0)

print(sample,np.shape(sample))








