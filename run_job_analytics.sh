# echo "re running setup.sh"

# source setup.sh

python Job_analytics.py -fileloc_rec "$REC_FILES" -fileloc_muons "$MUON_FILES" -fileloc_pairs "$PAIR_DATA" -num_pairs "$NUM_PAIRS" -num_cores "$NUM_CORES"

