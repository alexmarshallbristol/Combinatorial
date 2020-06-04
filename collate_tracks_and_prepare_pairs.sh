echo "re running setup.sh"

source setup.sh


echo "Running script: create_track_file_random_id.py"

python create_track_file_random_id.py -fileloc "$REC_FILES"

echo "tracks.root created"
echo "track_location_array.npy created"
echo "track_location_array_start_momentum.npy created"

echo

echo "Running script: Plot_track_initial_momentum.py"

python Plot_track_initial_momentum.py

echo

echo "Running script: get_tracks_from_file_random_id.py"

python get_tracks_from_file_random_id.py -fileloc "$REC_FILES"

echo "track_truth_data.npy created"

echo

echo "Running script: parallel_pair_job_information.py"

python parallel_pair_job_information.py -num_pairs "$NUM_PAIRS"

echo "array_of_unique_parirs.npy created"