

# Updated Code for SHiP Combinatorial Background Studies

Currently this repository contains the tools for creation of muon track pairs from muon input files. The full combinatorial background study requires more components, for example the analysis of signal samples, scripts studying cuts and rates of 5 years of SHiP, plotting and overlays of different samples. This code all exists and will all be added to this repository in time. 

## Installing the code:

- Clone this repository onto LXPLUS.

```bash
cd
mkdir Combinatorial
cd Combinatorial
git clone https://github.com/alexmarshallbristol/Combinatorial.git
```

- Clone and install [FairShip](https://github.com/ShipSoft/FairShip) into the same directory. 
```bash
git clone https://github.com/ShipSoft/FairShip
source /cvmfs/ship.cern.ch/SHiP-2020/latest/setUp.sh
aliBuild build FairShip --default fairship --always-prefer-system --config-dir $SHIPDIST
alienv enter FairShip/latest
```

- This repository comes with the 2020 [setup.sh](setup.sh) and [config.sh](config.sh) files, may have to recreate if FairShip has changed significantly.
```bash
rm config.sh
eval alienv load FairShip/latest > config.sh
```

## Running the code:

### Organising input muons.

First step is to organise a muon input sample. ** Using this repository straight out the box means you can only use up to 7500 input files (maximum  number of condor jobs queued at once).**

- Store muon samples in ROOT files (preferably each of approx 1 milion muons) on EOS. There are multiple potential sources of muon kinematics:
	- SHiP collaboration background files, at "/eos/experiment/ship/data/Mbias/background-prod-2018/pythia8_Geant4_10.0_withCharmandBeauty_*mu.root"
	- GAN muons, information for generation is presented in the [muGAN](https://github.com/alexmarshallbristol/muGAN) repository.
	- Muon flux measurement data? Located at "/eos/experiment/ship/user/truf/muflux-reco/RUN_8000_*" 

- Edit [setup.sh](setup.sh) to point the scripts to the location of muon input files, and the location to store various output files. 

### Running input muons in FairShip

- Run muons on FairShip with the [queue_run_muons.job](queue_run_muons.job) Condor jobscript. This should be configured by [setup.sh](setup.sh) to run a job for each input file.
```bash
condor_submit queue_run_muons.job
condor_q
```
- This will output files like "ship.conical.MuonBack-TGeant4_rec_*.root" at the REC_FILES location specified in [setup.sh](setup.sh).


### Collecting tracks and preparing pairs

- The bash script [collate_tracks_and_prepare_pairs.sh](collate_tracks_and_prepare_pairs.sh) runs the following python scripts:
	- create_track_file_random_id.py
		- Creates **tracks.root**, a ROOT file storing all track object from across all files.
		- Creates **track_location_array.npy**, a numpy file containing information about location of each track. Will allow access to MCTracks data later on. 
		- Also creates **track_location_array_start_momentum.npy**, a store of the initial momentum informaiton of each muon that made a good track.
	- Plot_track_initial_momentum.py
		- Example plotting script.
		- Plots information from **track_location_array_start_momentum.npy**
	- get_tracks_from_file_random_id.py
		- Skeleton script demonstrating how to get detailed simulation information about each muon that made a track. 
		- Creates **track_truth_data.npy** for this example.
	- parallel_pair_job_information.py
		- Creates **array_of_unique_parirs.npy** a list of unique pairs to be created in parallel in the next stage of analysis. 
		- The size of this list is dictated by NUM_PAIRS in [setup.sh](setup.sh).
```bash
. collate_tracks_and_prepare_pairs.sh
```


### Creating unique track pairs

- The list **array_of_unique_parirs.npy** contains information for what pairs to create.
- The option NUM_CORES in [setup.sh](setup.sh) indicates how many jobs to spread these over, running [setup.sh](setup.sh) should automatically configure the condor job script, [queue_create_pairs.job](queue_create_pairs.job). 
- To create pairs, queue the job script:
```bash
condor_submit queue_create_pairs.job
condor_q
```
- This will output file like "collected_pair_info_*.npy" to the location PAIR_DATA defined in [setup.sh](setup.sh).
- These arrays contain the following information about each muon pair:
	- **pair_weight**: weight_i times weight_j
	- **nmeas_i**: number of measurements for track i
	- **nmeas_j**: number of measurements for track j
	- **rchi2_i**: reduced chi2 value for track i
	- **rchi2_j**: reduced chi2 value for track j
	- **P_i**: total momentum of track i
	- **P_j**: total momentum of track j
	- **doca**: distance of closest approach between the two tracks
	- **fid**: bool for whether the reconstructed vertex was in the fiducial volume
	- **dist**: I.P w.r.t the target
	- **xv**: x coordinate of the reconstructed vertex
	- **yv**: y coordinate of the reconstructed vertex
	- **zv**: z coordinate of the reconstructed vertex
	- **np.sqrt(HNLMom[0]**2+HNLMom[1]**2+HNLMom[2]**2)** momentum of the reconstructed mother particle
	- **x_to_ip**: x component of I.P w.r.t the target
	- **y_to_ip**: y component of I.P w.r.t the target

### Combining output and plotting

- The bash script [Combine_output_and_plot.sh](Combine_output_and_plot.sh) runs the following python scripts:
	- combine_output.py
		- Combines the "collected_pair_info_*.npy" like files in the PAIR_DATA location into a single file **FULL_collected_pair_info.npy**.
	- Make_plots.py
		- Currently just a skeleton for a plotting script.


## Features to add

- Scripts to run and analyse any flavour of signal. 
- Complete plotting scripts, including comparison between 
- Combinatorial analysis scripts - location on hard drive for now. 
- Weighting of muons - previously removed for simplicity. 

