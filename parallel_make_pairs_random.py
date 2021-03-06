from __future__ import print_function
# example for accessing smeared hits and fitted tracks
import ROOT,os,sys,getopt
import rootUtils as ut
import shipunit as u
from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler
from rootpyPickler import Pickler
from decorators import *
import shipRoot_conf
shipRoot_conf.configure()
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math
import glob 
import pickle 
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('-jobid', action='store', dest='jobid', type=int,
					help='jobid')
parser.add_argument('-numberofjobs', action='store', dest='numberofjobs', type=int,
					help='numberofjobs')
parser.add_argument('-fileloc_rec', action='store', dest='fileloc_rec', type=str,
                                        help='fileloc_rec')
parser.add_argument('-fileloc_pair', action='store', dest='fileloc_pair', type=str,
                                        help='fileloc_pair')
results = parser.parse_args()
job_id = int(results.jobid)
number_of_jobs = int(results.numberofjobs)
fileloc_rec = results.fileloc_rec
fileloc_pair = results.fileloc_pair


#####

print('JobID =',job_id)

debug = False
chi2CutOff  = 4.
PDG = ROOT.TDatabasePDG.Instance()
inputFile  = None
geoFile    = None
dy         = None
nEvents    = 9999999
fiducialCut = True
measCutFK = 25
measCutPR = 22
docaCut = 2.

eosship = ROOT.gSystem.Getenv("EOSSHIP")


# geoFile = '/afs/cern.ch/user/a/amarshal/FairSHiP_run_GAN_muons/geofile_full.conical.MuonBack-TGeant4.root'
geoFile = 'geofile_full.conical.MuonBack-TGeant4.root'

# geoFile = '/afs/cern.ch/user/a/amarshal/FairSHiP_run_GAN_muons/geofile.root'
fgeo = ROOT.TFile(geoFile)

# new geofile, load Shipgeo dictionary written by run_simScript.py
upkl    = Unpickler(fgeo)
ShipGeo = upkl.load('ShipGeo')
ecalGeoFile = ShipGeo.ecal.File
dy = ShipGeo.Yheight/u.m

# -----Create geometry----------------------------------------------
import shipDet_conf
run = ROOT.FairRunSim()
run.SetName("TGeant4")  # Transport engine
run.SetOutputFile("dummy")  # Output file
run.SetUserConfig("g4Config_basic.C") # geant4 transport not used, only needed for the mag field
rtdb = run.GetRuntimeDb()
# -----Create geometry----------------------------------------------
print('a')
modules = shipDet_conf.configure(run,ShipGeo)
print('b')
run.Init()
print('c')
import geomGeant4
print('d')
if hasattr(ShipGeo.Bfield,"fieldMap"):
	fieldMaker = geomGeant4.addVMCFields(ShipGeo, '', True)
print('e')
sGeo   = ROOT.gGeoManager
print('f')
geoMat =  ROOT.genfit.TGeoMaterialInterface()
print('g')
ROOT.genfit.MaterialEffects.getInstance().init(geoMat)
print('h')
bfield = ROOT.genfit.FairShipFields()
print('i')
fM = ROOT.genfit.FieldManager.getInstance()
print('j')
fM.init(bfield)
print('k')
volDict = {}
i=0
for x in ROOT.gGeoManager.GetListOfVolumes():
	volDict[i]=x.GetName()
	i+=1
print('l')


h = {}
ut.bookHist(h,'delPOverP','delP / P',400,0.,200.,100,-0.5,0.5)
ut.bookHist(h,'pullPOverPx','delPx / sigma',400,0.,200.,100,-3.,3.)
ut.bookHist(h,'pullPOverPy','delPy / sigma',400,0.,200.,100,-3.,3.)
ut.bookHist(h,'pullPOverPz','delPz / sigma',400,0.,200.,100,-3.,3.)
ut.bookHist(h,'delPOverP2','delP / P chi2/nmeas<'+str(chi2CutOff),400,0.,200.,100,-0.5,0.5)
ut.bookHist(h,'delPOverPz','delPz / Pz',400,0.,200.,100,-0.5,0.5)
ut.bookHist(h,'delPOverP2z','delPz / Pz chi2/nmeas<'+str(chi2CutOff),400,0.,200.,100,-0.5,0.5)
ut.bookHist(h,'chi2','chi2/nmeas after trackfit',100,0.,10.)
ut.bookHist(h,'prob','prob(chi2)',100,0.,1.)
ut.bookHist(h,'IP','Impact Parameter',100,0.,10.)
ut.bookHist(h,'Vzresol','Vz reco - true [cm]',100,-50.,50.)
ut.bookHist(h,'Vxresol','Vx reco - true [cm]',100,-10.,10.)
ut.bookHist(h,'Vyresol','Vy reco - true [cm]',100,-10.,10.)
ut.bookHist(h,'Vzpull','Vz pull',100,-5.,5.)
ut.bookHist(h,'Vxpull','Vx pull',100,-5.,5.)
ut.bookHist(h,'Vypull','Vy pull',100,-5.,5.)
ut.bookHist(h,'Doca','Doca between two tracks',100,0.,10.)
ut.bookHist(h,'IP0','Impact Parameter to target',100,0.,100.)
ut.bookHist(h,'IP0/mass','Impact Parameter to target vs mass',100,0.,2.,100,0.,100.)
ut.bookHist(h,'HNL','reconstructed Mass',500,0.,2.)
ut.bookHist(h,'HNLw','reconstructed Mass with weights',500,0.,2.)
ut.bookHist(h,'meas','number of measurements',40,-0.5,39.5)
ut.bookHist(h,'meas2','number of measurements, fitted track',40,-0.5,39.5)
ut.bookHist(h,'measVSchi2','number of measurements vs chi2/meas',40,-0.5,39.5,100,0.,10.)
ut.bookHist(h,'distu','distance to wire',100,0.,1.)
ut.bookHist(h,'distv','distance to wire',100,0.,1.)
ut.bookHist(h,'disty','distance to wire',100,0.,1.)
ut.bookHist(h,'meanhits','mean number of hits / track',50,-0.5,49.5)
ut.bookHist(h,'ecalClusters','x/y and energy',50,-3.,3.,50,-6.,6.)

ut.bookHist(h,'extrapTimeDetX','extrapolation to TimeDet X',100,-10.,10.)
ut.bookHist(h,'extrapTimeDetY','extrapolation to TimeDet Y',100,-10.,10.)

ut.bookHist(h,'oa','cos opening angle',100,0.999,1.)
# potential Veto detectors
ut.bookHist(h,'nrtracks','nr of tracks in signal selected',10,-0.5,9.5)
ut.bookHist(h,'nrSVT','nr of hits in SVT',10,-0.5,9.5)
ut.bookHist(h,'nrUVT','nr of hits in UVT',100,-0.5,99.5)
ut.bookHist(h,'nrSBT','nr of hits in SBT',100,-0.5,99.5)
ut.bookHist(h,'nrRPC','nr of hits in RPC',100,-0.5,99.5)

import TrackExtrapolateTool

def VertexError(t1,t2,PosDir,CovMat,scalFac):
# with improved Vx x,y resolution
			a,u = PosDir[t1]['position'],PosDir[t1]['direction']
			c,v = PosDir[t2]['position'],PosDir[t2]['direction']
			Vsq = v.Dot(v)
			Usq = u.Dot(u)
			UV  = u.Dot(v)
			ca  = c-a
			denom = Usq*Vsq-UV**2
			tmp2 = Vsq*u-UV*v
			Va = ca.Dot(tmp2)/denom
			tmp2 = UV*u-Usq*v
			Vb = ca.Dot(tmp2)/denom
			X = (a+c+Va*u+Vb*v) * 0.5
			l1 = a - X + u*Va  # l2 = c - X + v*Vb
			dist = 2. * ROOT.TMath.Sqrt( l1.Dot(l1) )
			T = ROOT.TMatrixD(3,12)
			for i in range(3):
					for k in range(4):
							for j in range(3): 
								KD = 0
								if i==j: KD = 1
								if k==0 or k==2:
							# cova and covc
									temp  = ( u[j]*Vsq - v[j]*UV )*u[i] + (u[j]*UV-v[j]*Usq)*v[i]
									sign = -1
									if k==2 : sign = +1
									T[i][3*k+j] = 0.5*( KD + sign*temp/denom )
								elif k==1:
							# covu
									aNAZ = denom*( ca[j]*Vsq-v.Dot(ca)*v[j] )
									aZAN = ( ca.Dot(u)*Vsq-ca.Dot(v)*UV )*2*( u[j]*Vsq-v[j]*UV )
									bNAZ = denom*( ca[j]*UV+(u.Dot(ca)*v[j]) - 2*ca.Dot(v)*u[j] )
									bZAN = ( ca.Dot(u)*UV-ca.Dot(v)*Usq )*2*( u[j]*Vsq-v[j]*UV )
									T[i][3*k+j] = 0.5*( Va*KD + u[i]/denom**2*(aNAZ-aZAN) + v[i]/denom**2*(bNAZ-bZAN) )
								elif k==3:
							# covv
									aNAZ = denom*( 2*ca.Dot(u)*v[j] - ca.Dot(v)*u[j] - ca[j]*UV )
									aZAN = ( ca.Dot(u)*Vsq-ca.Dot(v)*UV )*2*( v[j]*Usq-u[j]*UV )
									bNAZ = denom*( ca.Dot(u)*u[j]-ca[j]*Usq ) 
									bZAN = ( ca.Dot(u)*UV-ca.Dot(v)*Usq )*2*( v[j]*Usq-u[j]*UV )
									T[i][3*k+j] = 0.5*(Vb*KD + u[i]/denom**2*(aNAZ-aZAN) + v[i]/denom**2*(bNAZ-bZAN) ) 
			transT = ROOT.TMatrixD(12,3)
			transT.Transpose(T)
			CovTracks = ROOT.TMatrixD(12,12)
			tlist = [t1,t2]
			for k in range(2):
					for i in range(6):
							for j in range(6): 
								xfac = 1.
								if i>2: xfac = scalFac[tlist[k]]  
								if j>2: xfac = xfac * scalFac[tlist[k]]
								CovTracks[i+k*6][j+k*6] = CovMat[tlist[k]][i][j] * xfac
								# if i==5 or j==5 :  CovMat[tlist[k]][i][j] = 0 # ignore error on z-direction
			tmp   = ROOT.TMatrixD(3,12)
			tmp.Mult(T,CovTracks)
			covX  = ROOT.TMatrixD(3,3)
			covX.Mult(tmp,transT)
			return X,covX,dist

from array import array
def dist2InnerWall(X,Y,Z):
		dist = 0
	# return distance to inner wall perpendicular to z-axis, if outside decayVolume return 0.
		node = sGeo.FindNode(X,Y,Z)
		if ShipGeo.tankDesign < 5:
					if not 'cave' in node.GetName(): return dist  # TP 
		else:
					if not 'decayVol' in node.GetName(): return dist
		start = array('d',[X,Y,Z])
		nsteps = 8
		dalpha = 2*ROOT.TMath.Pi()/nsteps
		rsq = X**2+Y**2
		minDistance = 100 *u.m
		for n in range(nsteps):
				alpha = n * dalpha
				sdir  = array('d',[ROOT.TMath.Sin(alpha),ROOT.TMath.Cos(alpha),0.])
				node = sGeo.InitTrack(start, sdir)
				nxt = sGeo.FindNextBoundary()
				if ShipGeo.tankDesign < 5 and nxt.GetName().find('I')<0: return 0    
				distance = sGeo.GetStep()
				if distance < minDistance  : minDistance = distance
		return minDistance

def isInFiducial(X,Y,Z):
			if Z > ShipGeo.TrackStation1.z : return False
			if Z < ShipGeo.vetoStation.z+100.*u.cm : return False
			# typical x,y Vx resolution for exclusive HNL decays 0.3cm,0.15cm (gaussian width)
			if dist2InnerWall(X,Y,Z)<5*u.cm: return False
			return True 
#
def ImpactParameter(point,tPos,tMom):
		t = 0
		if hasattr(tMom,'P'): P = tMom.P()
		else:                 P = tMom.Mag()
		for i in range(3):   t += tMom(i)/P*(point(i)-tPos(i)) 
		dist = 0
		for i in range(3):   dist += (point(i)-tPos(i)-t*tMom(i)/P)**2
		dist = ROOT.TMath.Sqrt(dist)
		return dist
#
def checkHNLorigin(sTree):
	flag = True
	if not fiducialCut: return flag
	flag = False
# only makes sense for signal == HNL
	hnlkey = -1
	for n in range(sTree.MCTrack.GetEntries()):
			mo = sTree.MCTrack[n].GetMotherId()
			if mo <0: continue
			if abs(sTree.MCTrack[mo].GetPdgCode()) == 9900015: 
							hnlkey = n
							break
	if hnlkey<0 : 
		print("checkHNLorigin: no HNL found")
	else:
		# MCTrack after HNL should be first daughter
		theHNLVx = sTree.MCTrack[hnlkey]
		X,Y,Z =  theHNLVx.GetStartX(),theHNLVx.GetStartY(),theHNLVx.GetStartZ()
		if isInFiducial(X,Y,Z): flag = True
	return flag 

def checkFiducialVolume(sTree,tkey,dy):
# extrapolate track to middle of magnet and check if in decay volume
			inside = True
			if not fiducialCut: return True
			fT = sTree.FitTracks[tkey]
			rc,pos,mom = TrackExtrapolateTool.extrapolateToPlane(fT,ShipGeo.Bfield.z)
			if not rc: return False
			if not dist2InnerWall(pos.X(),pos.Y(),pos.Z())>0: return False
			return inside
def getPtruthFirst(sTree,mcPartKey):
			Ptruth,Ptruthx,Ptruthy,Ptruthz = -1.,-1.,-1.,-1.
			for ahit in sTree.strawtubesPoint:
					if ahit.GetTrackID() == mcPartKey:
								Ptruthx,Ptruthy,Ptruthz = ahit.GetPx(),ahit.GetPy(),ahit.GetPz()
								Ptruth  = ROOT.TMath.Sqrt(Ptruthx**2+Ptruthy**2+Ptruthz**2)
								break
			return Ptruth,Ptruthx,Ptruthy,Ptruthz

def access2SmearedHits():
	key = 0
	for ahit in ev.SmearedHits.GetObject():
			print(ahit[0],ahit[1],ahit[2],ahit[3],ahit[4],ahit[5],ahit[6])
			# follow link to true MCHit
			mchit   = TrackingHits[key]
			mctrack =  MCTracks[mchit.GetTrackID()]
			print(mchit.GetZ(),mctrack.GetP(),mctrack.GetPdgCode())
			key+=1

def myVertex(t1,t2,PosDir):
	# closest distance between two tracks
				# d = |pq . u x v|/|u x v|
			# print(' ')
			# print('myvertex',PosDir)
			# print(np.shape(PosDir))
			# print(PosDir[0])
			# print(PosDir[0][0])
			a = ROOT.TVector3(PosDir[0][0](0) ,PosDir[0][0](1), PosDir[0][0](2))
			u = ROOT.TVector3(PosDir[0][1](0),PosDir[0][1](1),PosDir[0][1](2))
			c = ROOT.TVector3(PosDir[1][0](0) ,PosDir[1][0](1), PosDir[1][0](2))
			v = ROOT.TVector3(PosDir[1][1](0),PosDir[1][1](1),PosDir[1][1](2))
			pq = a-c
			uCrossv = u.Cross(v)
			dist  = pq.Dot(uCrossv)/(uCrossv.Mag()+1E-8)
			# u.a - u.c + s*|u|**2 - u.v*t    = 0
			# v.a - v.c + s*v.u    - t*|v|**2 = 0
			E = u.Dot(a) - u.Dot(c) 
			F = v.Dot(a) - v.Dot(c) 
			A,B = u.Mag2(), -u.Dot(v) 
			C,D = u.Dot(v), -v.Mag2()
			t = -(C*E-A*F)/(B*C-A*D)
			X = c.x()+v.x()*t
			Y = c.y()+v.y()*t
			Z = c.z()+v.z()*t
			return X,Y,Z,abs(dist)
def  RedoVertexing(t1,t2):    
	PosDir = [] 
	for tr in [t1,t2]:
		xx  = tr
		PosDir.append([xx.getPos(),xx.getDir()])

	xv,yv,zv,doca = myVertex(t1,t2,PosDir)
# as we have learned, need iterative procedure
	dz = 99999.
	reps,states,newPosDir = {},{},{}
	newPosDir = []
	parallelToZ = ROOT.TVector3(0., 0., 1.)
	rc = True 
	step = 0
	while dz > 0.1:
		zBefore = zv
		newPos = ROOT.TVector3(xv,yv,zv)
	# make a new rep for track 1,2
		for tr in [t1,t2]:     
			xx = tr
			reps[tr]   = ROOT.genfit.RKTrackRep(xx.getPDG())
			states[tr] = ROOT.genfit.StateOnPlane(reps[tr])
			reps[tr].setPosMom(states[tr],xx.getPos(),xx.getMom())
			try:
				reps[tr].extrapolateToPoint(states[tr], newPos, False)
			except:
				# print 'SHiPAna: extrapolation did not work'
				rc = False  
				break

			newPosDir.append([reps[tr].getPos(states[tr]),reps[tr].getDir(states[tr])])
	
		if not rc: break
		xv,yv,zv,doca = myVertex(t1,t2,newPosDir)
		dz = abs(zBefore-zv)
		step+=1
		if step > 10:  
					# print 'abort iteration, too many steps, pos=',xv,yv,zv,' doca=',doca,'z before and dz',zBefore,dz
					rc = False
					break 
	if not rc: return xv,yv,zv,doca # extrapolation failed, makes no sense to continue

	return xv,yv,zv,doca


def fitSingleGauss(x,ba=None,be=None):
				name    = 'myGauss_'+x 
				myGauss = h[x].GetListOfFunctions().FindObject(name)
				if not myGauss:
							if not ba : ba = h[x].GetBinCenter(1) 
							if not be : be = h[x].GetBinCenter(h[x].GetNbinsX()) 
							bw    = h[x].GetBinWidth(1) 
							mean  = h[x].GetMean()
							sigma = h[x].GetRMS()
							norm  = h[x].GetEntries()*0.3
							myGauss = ROOT.TF1(name,'[0]*'+str(bw)+'/([2]*sqrt(2*pi))*exp(-0.5*((x-[1])/[2])**2)+[3]',4)
							myGauss.SetParameter(0,norm)
							myGauss.SetParameter(1,mean)
							myGauss.SetParameter(2,sigma)
							myGauss.SetParameter(3,1.)
							myGauss.SetParName(0,'Signal')
							myGauss.SetParName(1,'Mean')
							myGauss.SetParName(2,'Sigma')
							myGauss.SetParName(3,'bckgr')
				h[x].Fit(myGauss,'','',ba,be) 

def match2HNL(p):
				matched = False
				hnlKey  = []
				for t in [p.GetDaughter(0),p.GetDaughter(1)]: 
						mcp = sTree.fitTrack2MC[t]
						while mcp > -0.5:
								mo = sTree.MCTrack[mcp]
								if abs(mo.GetPdgCode()) == 9900015:
											hnlKey.append(mcp)
											break  
								mcp = mo.GetMotherId()
				if len(hnlKey) == 2: 
							if hnlKey[0]==hnlKey[1]: matched = True
				return matched
def ecalCluster2MC(aClus):
	# return MC track most contributing, and its fraction of energy
		trackid    = ROOT.Long()
		energy_dep = ROOT.Double()
		mcLink = {}
		for i in range( aClus.Size() ):
				mccell = ecalStructure.GetHitCell(aClus.CellNum(i))  # Get i'th cell of the cluster.
				for n in range( mccell.TrackEnergySize()):
						mccell.GetTrackEnergySlow(n, trackid, energy_dep)
						if not abs(trackid)<sTree.MCTrack.GetEntries(): tid = -1
						else: tid = int(trackid)
						if not mcLink.has_key(tid): mcLink[tid]=0
						mcLink[tid]+=energy_dep
# find trackid most contributing
		eMax,mMax = 0,-1
		for m in mcLink:
					if mcLink[m]>eMax:
								eMax = mcLink[m]
								mMax = m
		return mMax,eMax/aClus.Energy()


# calculate z front face of ecal, needed later
top = ROOT.gGeoManager.GetTopVolume()
ecal = None
if top.GetNode('Ecal_1'):
	ecal = top.GetNode('Ecal_1')
	z_ecal = ecal.GetMatrix().GetTranslation()[2]
elif top.GetNode('SplitCalDetector_1'):
	ecal = top.GetNode('SplitCalDetector_1')
	z_ecal = ecal.GetMatrix().GetTranslation()[2]

# start event loop

def ImpactParameter2(point,tPos,tMom):
		t = 0
		# if hasattr(tMom,'P'): P = tMom.P()
		# else:                 P = tMom.Mag()
		P = math.sqrt(tMom[0]**2 + tMom[1]**2 + tMom[2]**2)
		for i in range(3):   t += tMom[i]/P*(point(i)-tPos[i]) 
		dist = 0
		for i in range(3):   dist += (point[i]-tPos[i]-t*tMom[i]/P)**2
		dist = ROOT.TMath.Sqrt(dist)
		return dist
		
def ImpactParameter_x_y(point,tPos,tMom):
		t = 0
		# if hasattr(tMom,'P'): P = tMom.P()
		# else:                 P = tMom.Mag()
		P = math.sqrt(tMom[0]**2 + tMom[1]**2 + tMom[2]**2)
		for i in range(3):   t += tMom[i]/P*(point(i)-tPos[i]) 

		
		x = point[0]-tPos[0]-t*tMom[0]/P
		y = point[1]-tPos[1]-t*tMom[1]/P
		z = point[2]-tPos[2]-t*tMom[2]/P

		return x, y, z


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def create_pair(i,j, weight_i, weight_j):

	'''
		Load correct tracks from file, based on indexes i and j
	'''
	# print('creating pair',i,j,weight_i,weight_j)
	try:
		key_i = tracks_file.GetListOfKeys()[i]
		get_track_string = 'track'+find_between(str(key_i),"track"," ")+';1'
		track_i = tracks_file.Get(get_track_string)

		# track_i = tracks_file.Get(str(key_i)[str(key_i).find('"')+1:str(key_i)[str(key_i).find('"')+1:].find('"')-len(str(key_i)[str(key_i).find('"')+1:])]+";1") 

		

		fitStatus_i   = track_i.getFitStatus()
		fittedState_i = track_i.getFittedState()

		# track_j = tracks_file.Get(str(key_j)[str(key_j).find('"')+1:str(key_j)[str(key_j).find('"')+1:].find('"')-len(str(key_j)[str(key_j).find('"')+1:])]+";1") 
		
		key_j = tracks_file.GetListOfKeys()[j]
		get_track_string = 'track'+find_between(str(key_j),"track"," ")+';1'
		track_j = tracks_file.Get(get_track_string)

		fitStatus_j   = track_j.getFitStatus()
		fittedState_j = track_j.getFittedState()






		'''
			Can now play with track properties...
		'''


		'''
			Get nmeas and reduced chi2
		'''
		nmeas_i = fitStatus_i.getNdf()
		nmeas_j = fitStatus_j.getNdf()
		chi2_i = fitStatus_i.getChi2()
		prob_i = ROOT.TMath.Prob(chi2_i,int(nmeas_i))
		rchi2_i = chi2_i/nmeas_i
		chi2_j = fitStatus_j.getChi2()
		prob_j = ROOT.TMath.Prob(chi2_j,int(nmeas_j))
		rchi2_j = chi2_j/nmeas_j

		'''
			Reconstructed momentum
		'''

		P_i= fittedState_i.getMomMag()
		P_j = fittedState_j.getMomMag()

		'''
			Need to check there are digi hits in straw tubes before and after magnet, for example:
				hits_before_and_after_i = 1 yes
				hits_before_and_after_i = 0 no

			Past this point sTree_i and sTree_j can be used to access MC truth hits for each track
		'''
		'''
	 	id_num_i = np.where(track_location_array == str(key_i)[str(key_i).find('"')+1:str(key_i)[str(key_i).find('"')+1:].find('"')-len(str(key_i)[str(key_i).find('"')+1:])])[0][0]
	 	# print(track_location_array,id_num_i)

	 	file_random_id_i = int(list_of_file_ID[int(track_location_array[id_num_i][0])])
		specific_file_i = file_path_start + str(file_random_id_i) + file_path_end
		event_id_i = int(track_location_array[i][1])

		# print('specific_file_i',specific_file_i)
		

		f_i = ROOT.TFile(str(specific_file_i),"read")

		sTree_i = f_i.cbmsim
		sTree_i.GetEntry(event_id_i)
		hits_in_straw_stations_i = np.zeros(4)
		for ahit in sTree_i.Digi_StrawtubesHits:
			detID = ahit.GetDetectorID()
			if int(str(detID)[:1]) == 1:
				hits_in_straw_stations_i[0] = 1
			if int(str(detID)[:1]) == 2:
				hits_in_straw_stations_i[1] = 1
			if int(str(detID)[:1]) == 3:
				hits_in_straw_stations_i[2] = 1
			if int(str(detID)[:1]) == 4:
				hits_in_straw_stations_i[3] = 1
		hits_before_and_after_i = 0
		if hits_in_straw_stations_i[0] == 1 or hits_in_straw_stations_i[1] == 1:
			if hits_in_straw_stations_i[2] == 1 or hits_in_straw_stations_i[3] == 1:
				hits_before_and_after_i = 1


		id_num_j = np.where(track_location_array == str(key_j)[str(key_j).find('"')+1:str(key_j)[str(key_j).find('"')+1:].find('"')-len(str(key_j)[str(key_j).find('"')+1:])])[0][0]
	 	file_random_id_j = int(list_of_file_ID[int(track_location_array[id_num_j][0])])
		specific_file_j = file_path_start + str(file_random_id_j) + file_path_end
		event_id_j = int(track_location_array[j][1])

		# print('specific_file_j',specific_file_j)
		
		f_j = ROOT.TFile(str(specific_file_j),"read")

		sTree_j = f_j.cbmsim
		sTree_j.GetEntry(event_id_j)
		hits_in_straw_stations_j = np.zeros(4)
		for ahit in sTree_j.Digi_StrawtubesHits:
			detID = ahit.GetDetectorID()
			if int(str(detID)[:1]) == 1:
				hits_in_straw_stations_j[0] = 1
			if int(str(detID)[:1]) == 2:
				hits_in_straw_stations_j[1] = 1
			if int(str(detID)[:1]) == 3:
				hits_in_straw_stations_j[2] = 1
			if int(str(detID)[:1]) == 4:
				hits_in_straw_stations_j[3] = 1
		hits_before_and_after_j = 0
		if hits_in_straw_stations_j[0] == 1 or hits_in_straw_stations_j[1] == 1:
			if hits_in_straw_stations_j[2] == 1 or hits_in_straw_stations_j[3] == 1:
				hits_before_and_after_j = 1
		'''
		'''
			Use RedoVertexing() to produce DOCA and Fiducial bool: 1 yes and 0 no
		'''

		pair = [fittedState_i,fittedState_j]
		xv,yv,zv,doca = RedoVertexing(pair[0],pair[1])
		fid = isInFiducial(xv,yv,zv)
		if fid == True:
			fid = 1
		elif fid == False:
			fid = 0

		'''
			Combine momentum of the two tracks to create HNLMom, use with HNLPos in ImpactParameter2() to get dist
		'''

		mom_i = [pair[0].getMom()[0],pair[0].getMom()[1],pair[0].getMom()[2]]
		mom_j = [pair[1].getMom()[0],pair[1].getMom()[1],pair[1].getMom()[2]]

		HNLPos = [xv,yv,zv]

		HNLMom = [mom_i[0]+mom_j[0],mom_i[1]+mom_j[1],mom_i[2]+mom_j[2]]

		# # HNLMom = [sum of momentum of charged tracks]
		tr = ROOT.TVector3(0,0,ShipGeo.target.z0)
		dist = ImpactParameter2(tr,HNLPos,HNLMom)

		'''
			Get initial momentum of each muon in the target - will use this for KDE GAN weights later on
		'''

		pair_weight = weight_i*weight_j



		'''

		Cuts: DO NOT CUT - SAVE ALL

			- P -
			- straw digi hits before and after magnet
			- nmeas -
			- chi2/dof -
			- DOCA -
			- fiducial -
			- IP -

		Hits:

			- Tailor to whatever interested in
			- p vs pt when striking SBT (study for vessel DIS)
			- patterns/hot spots in SBT and RPC hits 


		Upstream systems:

			- Extrapolate to RPC and SBT
			- Compare to digi hits

		Initial momentum in SHiP target:

			- used for KDE weights

		'''
		x_to_ip, y_to_ip, z_to_ip = ImpactParameter_x_y(tr,HNLPos,HNLMom)
		pair_information = [pair_weight, nmeas_i, nmeas_j, rchi2_i, rchi2_j, P_i, P_j, doca, fid, dist, xv, yv, zv, np.sqrt(HNLMom[0]**2+HNLMom[1]**2+HNLMom[2]**2),x_to_ip, y_to_ip]
		worked_bool = True

	except:
		worked_bool = False
		pair_information = 0
	return worked_bool, pair_information


import shipVeto


#####

print('JobID =',job_id)

track_location_array = np.load('track_location_array.npy')

tracks_file = ROOT.TFile("tracks.root","read")


file_path_start = '%sship.conical.MuonBack-TGeant4_rec_'%fileloc_rec
file_path_end = '.root'

# GAN_weights = np.load('GAN_weights.npy')

array_of_unique_parirs = np.load('array_of_unique_parirs.npy')


fileloc_pair = results.fileloc_pair




per_job = np.floor(np.shape(array_of_unique_parirs)[0]/number_of_jobs)

this_job = per_job*job_id


array_of_unique_parirs = array_of_unique_parirs[int(this_job):int(this_job+per_job)]


number_of_fittracks = float(np.shape(track_location_array)[0])


pairs_run_through = 0




collected_pair_info = np.empty((0,16))

np.save('collected_pair_info_%d'%job_id,collected_pair_info)

for unique_pair in array_of_unique_parirs[1:]:

	try:
		i = unique_pair[0]
		j = unique_pair[1]
		worked_bool,pair_info = create_pair(i,j,1,1)

		if worked_bool == True:
			pairs_run_through += 1
			collected_pair_info = np.append(collected_pair_info, [pair_info], axis=0)

		if pairs_run_through%100 == 0:
			print(pairs_run_through)

		if pairs_run_through%500 == 0:
			saved_array = np.load('collected_pair_info_%d.npy'%job_id)
			collected_pair_info = np.concatenate((saved_array, collected_pair_info),axis=0)
			np.save('collected_pair_info_%d'%job_id,collected_pair_info)
			collected_pair_info = np.empty((0,16))

		if pairs_run_through%2500 == 0:
			shutil.copyfile('collected_pair_info_%d.npy'%job_id,'%sTMP_collected_pair_info_%d.npy'%(fileloc_pair,job_id))
					
	except:
		print(unique_pair, 'fail')



print(pairs_run_through)

print(np.shape(collected_pair_info))

saved_array = np.load('collected_pair_info_%d.npy'%job_id)
collected_pair_info = np.concatenate((saved_array, collected_pair_info),axis=0)
np.save('collected_pair_info_%d'%job_id,collected_pair_info)
shutil.copyfile('collected_pair_info_%d.npy'%job_id,'%sTMP_collected_pair_info_%d.npy'%(fileloc_pair,job_id))

shutil.move('%sTMP_collected_pair_info_%d.npy'%(fileloc_pair,job_id),'%scollected_pair_info_%d.npy'%(fileloc_pair,job_id))

print('Complete pair creation.')






