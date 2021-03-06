#Template for maniupulating Nbody Star Cluster simulations
import nbodypy as npy
import sys,os

#Set files to read in simulation
filepath=''
bfilename='fort.82'
sfilename='fort.83'

#If not in current directory, check for a /start directory
if not os.path.isfile(sfilename):
    filepath+='./start/'

#Open files to read
f82=open(filepath+bfilename,'r')
f83=open(filepath+sfilename,'r')

#Open files to write
out3d=open('dalpha_prof_m30.dat','w')
out2d=open('dalpha_prof_m30_pro.dat','w')

#Get first snapshot
#Can edit whether or not key_params should be calculated and if units should be converted
cluster=npy.get_nbody6_jarrod(f82,f83,do_keyparams=True)
npy.nbody_to_realpc(cluster)

#Loop through all timesteps and/or to a specific timestep
while cluster.ntot>0.0 and cluster.tphys<=12000.0:
    print(cluster.tphys,cluster.ntot)
    out3d.write("%f " % cluster.tphys)
    out2d.write("%f " % cluster.tphys)
    #OPERATE ON TIMESTEP HERE*************************************
    lrprofn,aprof,dalpha,edalpha,ydalpha,eydalpha=npy.alpha_prof(cluster,mmin=0.35,mmax=0.75,nmass=10,projected=False,obs_cut='M30')
    lrprofn_pro,aprof_pro,dalpha_pro,edalpha_pro,ydalpha_pro,eydalpha_pro=npy.alpha_prof(cluster,mmin=0.35,mmax=0.75,nmass=10,projected=True,obs_cut='M30')

    for i in range(0,len(lrprofn)):
        out3d.write("%f ",lrprofn[i])
        out2d.write("%f ",lrprofn_pro[i])
    for i in range(0,len(lrprofn)):
        out3d.write("%f ",aprof[i])
        out2d.write("%f ",aprof_pro[i])

    out3d.write("%f %f %f %f\n" % (dalpha,edalpha,ydalpha,eydalpha))
    out2d.write("%f %f %f %f\n" % (dalpha_pro,edalpha_pro,ydalpha_pro,eydalpha_pro))

    #Read in next timestep****************************************
    cluster=npy.get_nbody6_jarrod(f82,f83,do_keyparams=False)
    npy.nbody_to_realpc(cluster)

    #Check for restart directory
    if cluster.ntot==0:
        f82.close()
        f83.close()
        filepath+='cont/'
        if os.path.isfile(filepath+sfilename):
            f82=open(filepath+bfilename,'r')
            f83=open(filepath+sfilename,'r')
            cluster=npy.get_nbody6_jarrod(f82,f83,do_keyparams=True)
            npy.nbody_to_realpc(cluster)
