
--------------------------------------------------------------------------------------------------------------------------------------------
/eos/experiment/ship/user/amarshal/afs_folders/FairSHiP_run_GAN_muons

	OVERALL STEPS

--------------------------------------------------------------------------------------------------------------------------------------------

	- [SLOW] Generate GAN muons on Blue Crystal and scp them to /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id/
		- If you are generating more after muons in above directory are already run, you must generate new muons to a new directory.. say /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id2/. After this step you can put output of FairSHiP in the same directory: /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_FairSHiP/ (beacuse unlikely to have same 9 digit random_id).
	
		**** Can repeat the above step to add to statistics **** - probably never will as currently will have 3E8 pairs of background muons - will need to simulate a lot of signal to compare this to. basically unlimited background pairs to train a classifer on


	- [INST] Count number of generated files in a directory and create list_of_file_ID.npy - each condor_submit can only look at one directory and only use one list_of_file_ID.npy file
	- [MED] Run GAN muons down FairSHiP with 'SIMULATION FILES:' below
		- output is reconstructed files in /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_FairSHiP/
	- [INST] Count number of fittracks in /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_FairSHiP/
	- [INST] Decide number of cores to work on, create a job_order.npy file.
	- [FAST] Run parallel pair creating code
	- [INST] Combine and plot results.


			NOTE: EVEN WITH GAN THE SLOWEST STEP IS STILL GENERATING MUONS - MOSTLY DUE TO LACK OF ACCESS TO GPUs

--------------------------------------------------------------------------------------------------------------------------------------------

	RUNNING GAN GENERATED MUONS THROUGH FAIRSHIP AND ANALYSING MUONS THAT PRODUCE TRACKS

--------------------------------------------------------------------------------------------------------------------------------------------

	SIMULATION FILES:

		fairship.tar.gz
			- contains correct Z start position in shipgen/MuonBackGenerator.cxx
			- macro/ShipReco.py creates Reco_finished.txt correctly

		queue_run_GAN_muons.job
			- queues FairSHiP running of files in /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id/*
			- full run is 'queue 21431' (ls -l /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id/* | wc -l)
			- transfer_input_files=fairship.tar.gz,convert.py,list_of_file_ID.npy,copy_file.py,copy_file_post.py
			- each job takes ~ 5-6 hrs

		convert.py
			- converts .npy file (GAN ouput) to .root files (accepted by MuonBackGenerator.cxx)

		list_of_file_ID.npy
			- created by glob_random_id_files.py
			- list of random_ids, e.g '100789780'
			- information in this file defines the file id system 
			- file must be recreated if more GAN .npy files are added to /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id/

		copy_file.py
			- file run on each job 
			- takes -jobid and checks against list_of_file_ID.npy, copies correct input file from /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id/

		copy_file_post.py
			- file run on each job 
			- takes -jobid and copies reconstructed output file ship.conical.MuonBack-TGeant4_rec.root to correct ouput name in /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_FairSHiP/

		run_muons_exe
			- executable for each condor job
			- relies on environment variable "$id"/jobid

--------------------------------------------------------------------------------------------------------------------------------------------

	GENERAL REQUIRED FILES:

		geofile_full.conical.Pythia8-TGeant4.root
			- geometry file outputted by FairSHiP
			- required for track and hit analysis 

--------------------------------------------------------------------------------------------------------------------------------------------

	ORGANISING OUTPUT FILES:

		create_track_file_random_id.py
			- loops through all outputted files glob.glob('/eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_FairSHiP/*'). Note, the code is immune to missing output files (failed jobs)
			- currently this file runs cuts on track properties: can be edited 
			- creates output files: tracks.root and track_location_array.npy
			tracks.root
				- saved root track objects for every track
			track_location_array.npy
				- information about track location in reco files, this information will be needed in get_tracks_from_file_random_id.py

--------------------------------------------------------------------------------------------------------------------------------------------

	ANALYSIS FILES:

		get_tracks_from_file_random_id.py
			- uses tracks.root and track_location_array.npy to quickly access all muons that produced tracks 
			- uses list_of_file_ID.npy to cycle through any reco files to access hits 
			- can produce plots of track properties and truth level muon hits for muons that procuded tracks 
			- examples for how to access/plot hits are inside the code of this script. 
			- saves track_truth_data.npy containing the following information for each track:
				[weight, x_i, y_i, z_i, px_i, py_i, pz_i, sbt_bool, rpc_bool, x_ves, y_ves, z_ves, px_ves, py_ves, pz_ves, reco_mom, reco_mom_T]

		GAN_KDE_ratio.npy
			- currently this is /Users/am13743/Desktop/Data_for_GAN_paper_plots/ratio_35_small.npy

		x_values_bins_limits_35.npy and y_values_bins_limits_35.npy
			- bin edge values used in get_tracks_from_file_random_id.py to pull weight from GAN_KDE_ratio.npy for correct bin

		checking_GAN_KDE.py
			- checking orientation of ratio array is correct, output is test_KDE_ratio.png

		get_ratio_for_weight_normalisation_35.py
			- calculates the normalisation required to be applied to weights to maintain same muons/POT

		track_truth_data.npy
			- contains single track information, used by parallel_make_pairs.py script - instead of recalculating weight every pair. 

		PARALLEL MAKE PAIRS FILES:

			parallel_pair_job_information.py 
				- serial job, no pairs (fast) - basically example code
				- inputs are number of fittracks and number of jobs planned
				- 45k pairs was roughly 10 minutes (previous full sim combi analysis)
				- creates pair creation order for each job into file job_order.npy
				- at the end is an example of code on each job using job_order.npy or work out which pairs to work on

			job_order.npy
				- structure: [job_id, start_major, start_minor] where a pair =[major, minor]

			fairship.tar.gz
				- still need to build fairship to access ShipAna.py functions that are used in parallel_make_pairs.py

			queue_muon_pairs.job
				- run pairs analysis in parallel 
				- must communicate the number of jobs queued with values in parallel_make_pairs.py
				- must transfer geo file: geofile_full.conical.Pythia8-TGeant4.root
				- transfer job order

			muon_pairs_exe
				- executable for condor
				- NOT COMPLETE FILE YET - need to understand what output of parallel_make_pairs.py will look like

			parallel_make_pairs.py
				- uses job_order.npy and -jobid to only loop over (keys of muons) pairs a specific job is required to compute
				- loops over keys (keys point to tracks) in tracks.root
				- function create_pair() computes calculations on each pair - currently this function is not written
				- saves outputted information to /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_pairs/
				- uses track_truth_data.npy to access muon weight information
				- pair information array: [pair_weight, nmeas_i, nmeas_j, rchi2_i, rchi2_j, P_i, P_j, hits_before_and_after_i, hits_before_and_after_j, doca, fid, dist, xv, yv, zv, HNL_mom]

			combine_pairs_output_information.py - NOT WRITTEN YET
				- combines files in /eos/experiment/ship/user/amarshal/HUGE_GAN_random_id_pairs/

			plot_pairs_output_information.py 
				- plot combined pairs information from file produced by combine_pairs_output_information.py
				- get_errors() function returns normalized histogram enteries, with weighted errors -> sqrt(sum(weights**2))

--------------------------------------------------------------------------------------------------------------------------------------------

WILL I EVENTUALLY ALSO WANT TO WEIGHT EVERYTHING TO ONE SPILL? THIS CORRECTION WOULD BE APPLIED IN get_tracks_from_file_random_id.py as say a factor of 1/0.7 if 70% of a spill was simulated

