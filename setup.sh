echo 

echo "Setting up environment variables..."

echo 

SHIPBUILD_location=/afs/cern.ch/user/a/amarshal/Combinatorial

# MUON_FILES="/eos/experiment/ship/user/amarshal/AUX_GANs_output/muons_*.root"

# REC_FILES="/eos/experiment/ship/user/amarshal/AUX_GANs_output/"

# PAIR_DATA="/eos/experiment/ship/user/amarshal/AUX_GANs_output/"

MUON_FILES="/eos/experiment/ship/user/amarshal/muflux_root_1M/muflux_*.root"

REC_FILES="/eos/experiment/ship/user/amarshal/muflux_root_1M/"

PAIR_DATA="/eos/experiment/ship/user/amarshal/muflux_root_1M/"

echo "FairShip located at: $SHIPBUILD_location"
# echo "Muon files are located at: $MUON_FILES, where there are currently $(ls -l $MUON_FILES | wc -l) files."
echo "Reconstructed files will be saved to: $REC_FILES"
echo "Combinatorial muon pair data will be saved to: $PAIR_DATA"

echo

echo "When running muons, each file will be run on an individual core (can only run up to 7500)."

# sed -i "/queue/c\queue $(ls -l $MUON_FILES | wc -l)" queue_run_muons.job

echo 

NUM_PAIRS=100
NUM_CORES=1

echo "When creating pairs, $NUM_PAIRS pairs will be created. This will spead over $NUM_CORES cores."

sed -i "/queue/c\queue $NUM_CORES" queue_create_pairs.job

echo

echo "Sourcing FairShip..."

source /cvmfs/ship.cern.ch/SHiP-2020/latest/setUp.sh
export ALIBUILD_WORK_DIR=$SHIPBUILD_location/sw
source $SHIPBUILD_location/config.sh

echo 
