#Determine radial profiles of key properties

import numpy as np
from galpy.util import bovy_coords

from constants import *
from recipes import *
from operations import *
from plots import *
from coordinates import rect_to_sphere

def rho_prof(cluster,mmin=None,mmax=None,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=15,indx=None,projected=False,obs_cut=None,plot=False,**kwargs):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()


    rprof=np.array([])
    pprof=np.array([])
    nprof=np.array([])

    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    if indx==None:
        indx=(cluster.id > -1)

    #Build subcluster containing only stars in the full radial and mass range:
    indx*=(r >= rmin) * (r <= rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)

    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(r[indx],nrad)

    for i in range(0,len(r_mean)):
        rindx=indx * (r >= r_lower[i]) * (r <= r_upper[i])
        rprof=np.append(rprof,r_mean[i])
        if projected:
            vol=np.pi*(r_upper[i]**2-r_lower[i]**2.)
        else:
            vol=(4./3.)*np.pi*(r_upper[i]**3-r_lower[i]**3.)

        pprof=np.append(pprof,np.sum(cluster.m[rindx]/vol))
        nprof=np.append(nprof,np.sum(rindx))


    if plot:
        filename=kwargs.pop('filename',None)   
        overplot=kwargs.pop('overplot',False)        
     
        if cluster.units=='nbody':
            xunits=' (NBODY)'
            yunits=' (NBODY)'
        elif cluster.units=='realpc':
            xunits=' (pc)'
            if projected:
                yunits=' Msun/pc^2'
            else:
                yunits=' Msun/pc^3'
        elif cluster.units=='realkpc':
            xunits=' (kpc)'
            if projected:
                yunits=' Msun/kpc^2'
            else:
                yunits=' Msun/kpc^3'
        elif cluster.units=='galpy':
            xunits=' (GALPY)'
            yunits=' (GALPY)'

        else:
            xunits=''
            yunits=''

        x,y,n=rprof,pprof,nprof
        nlplot(x,y,xlabel='R'+xunits,ylabel='rho'+yunits,title='Time = %f' % cluster.tphys,log=True,overplot=overplot,filename=filename)

        if filename!=None:
            plt.savefig(filename)

    return_cluster(cluster,units0,origin0,center0)

    return rprof,pprof,nprof

def m_prof(cluster,mmin=None,mmax=None,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=15,indx=None,projected=False,cumulative=False,obs_cut=None):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()

    rprof=[]
    mprof=[]
    nprof=[]

    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    if indx==None:
        indx=(cluster.id > -1)

    #Build subcluster containing only stars in the full radial and mass range:
    indx*=(r >= rmin) * (r<=rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)

    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(r[indx],nrad)

    for i in range(0,len(r_mean)):
        if cumulative:
            rindx=indx * (r <= r_upper[i])
        else:
            rindx=indx * (r >= r_lower[i]) * (r <= r_upper[i])
        rprof.append(r_mean[i])

        mprof.append(np.sum(cluster.m[rindx]))
        nprof.append(np.sum(rindx))

    return_cluster(cluster,units0,origin0,center0)

    return rprof,mprof,nprof


#Measure the radial variation in the stellar mass function
#Mass range optional
#Radial range optional
#Stellar evolution range (kw type) optional (default is MS stars)
def alpha_prof(cluster,mmin=None,mmax=None,nmass=10,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=1,indx=None,projected=False,obs_cut=None,plot=False,**kwargs):

    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()


    lrprofn=[]
    aprof=[]
    
    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    if indx==None:
        indx=(cluster.id > -1)

    #Build subcluster containing only stars in the full radial and mass range:
    indx*=(r >= rmin) * (r<=rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)

    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(r[indx],nrad)

    for i in range(0,len(r_mean)):
        rindx=indx * (r >= r_lower[i]) * (r <= r_upper[i])

        m_mean,m_hist,dm,alpha,ealpha,yalpha,eyalpha=dx_function(cluster.m[rindx],nmass)

        if alpha > -100:
            if projected:
                lrprofn.append(np.log(r_mean[i]/cluster.rmpro))
            else:
                lrprofn.append(np.log(r_mean[i]/cluster.rm))

            aprof.append(alpha)

    if len(lrprofn)>3:
        (dalpha,ydalpha),V=np.polyfit(lrprofn,aprof,1,cov=True)
        edalpha=np.sqrt(V[0][0])
        eydalpha=np.sqrt(V[1][1])
    else:
        dalpha=-100.0
        ydalpha=0.0
        edalpha=0.0
        eydalpha=0.0

    if plot:
        filename=kwargs.pop('filename',None)
        overplot=kwargs.pop('overplot',False)        

        nplot(lrprofn,aprof,xlabel=r'$\ln(r/r_m)$',ylabel=r'$\alpha$',overplot=overplot,**kwargs)
        rfit=np.linspace(np.min(lrprofn),np.max(lrprofn),nrad)
        afit=dalpha*rfit+ydalpha
        nlplot(rfit,afit,overplot=True,label=(r'd$\alpha$ = %f' % dalpha))
        plt.legend()

        if filename!=None:
            plt.savefig(filename)

    cluster.dalpha=dalpha

    return_cluster(cluster,units0,origin0,center0)

    return lrprofn,aprof,dalpha,edalpha,ydalpha,eydalpha

#Measure the radial variation in the velocity dispersion
#Mass range optional
#Radial range optional
#Stellar evolution range (kw type) optional (default is all stars)
def sigv_prof(cluster,mmin=None,mmax=None,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=15,projected=False,obs_cut=None):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()


    lrprofn=[]
    sigvprof=[]
    betaprof=[]

    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    #Build subcluster containing only stars in the full radial and mass range:
    indx=(r >= rmin) * (r<=rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)

    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)
   
    #Convert to cylindrical or spherical coordinates:
    if projected:
        r,theta,z=bovy_coords.rect_to_cyl(cluster.x,cluster.y,cluster.z)
        vr,vtheta,vz=bovy_coords.rect_to_cyl_vec(cluster.vx,cluster.vy,cluster.vz,cluster.x,cluster.y,cluster.z)
    else:
        r,theta,phi,vr,vt,vp=rect_to_sphere(cluster)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(r[indx],nrad)

    for i in range(0,len(r_mean)):
        rindx=indx * (r >= r_lower[i]) * (r <= r_upper[i])

        if np.sum(rindx) > 3.:

            sigr=np.std(vr[rindx])
            sigt=np.std(vt[rindx])

            if projected:
                sigp=np.zeros(len(vr))
                beta=sigt/sigr-1.
            else:
                sigp=np.std(vp[rindx])
                beta=1.0-(sigt**2.0+sigp**2.0)/(2.*(sigr**2.0))
            
            sigv=np.sqrt(sigr**2.0+sigt**2.0+sigp**2.0)

            if projected:
                lrprofn.append(np.log(r_mean[i]/cluster.rmpro))
            else:
                lrprofn.append(np.log(r_mean[i]/cluster.rm))

            sigvprof.append(sigv)
            betaprof.append(beta)
           

    return_cluster(cluster,units0,origin0,center0)
     
    return lrprofn,sigvprof,betaprof

def v_prof(cluster,mmin=None,mmax=None,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=15,indx=None,projected=False,obs_cut=None):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()

    lrprofn=[]
    sigvprof=[]

    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    if indx==None:
        indx=(cluster.id > -1)

    #Build subcluster containing only stars in the full radial and mass range:
    indx*=(r >= rmin) * (r<=rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)
  
    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)

    #Convert to cylindrical or spherical coordinates:
    if projected:
        r,theta,z=bovy_coords.rect_to_cyl(cluster.x,cluster.y,cluster.z)
        vr,vtheta,vz=bovy_coords.rect_to_cyl_vec(cluster.vx,cluster.vy,cluster.vz,cluster.x,cluster.y,cluster.z)
    else:
        r,theta,phi,vr,vt,vp=rect_to_sphere(cluster)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(r[indx],nrad)

    for i in range(0,len(r_mean)):
        rindx=indx * (r >= r_lower[i]) * (r <= r_upper[i])

        if np.sum(rindx) > 3.:

            vrmean=np.mean(vr[rindx])
            vtmean=np.mean(vt[rindx])

            if projected:
                vpmean=np.zeros(len(vr))
            else:
                vpmean=np.mean(vp[rindx])
            
            vmean=np.sqrt(vrmean**2.0+vtmean**2.0+vpmean**2.0)

            if projected:
                lrprofn.append(np.log(r_mean[i]/cluster.rmpro))
            else:
                lrprofn.append(np.log(r_mean[i]/cluster.rm))

            vprof.append(vmean)

    return_cluster(cluster,units0,origin0,center0)

    return lrprofn,vprof

def eta_prof(cluster,mmin=None,mmax=None,nmass=10,rmin=None,rmax=None,nrad=20,vmin=None,vmax=None,emin=None,emax=None,kwmin=0,kwmax=1,indx=None,projected=False,obs_cut=None):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_center()

    lrprofn=[]
    eprof=[]
    
    if projected:
        r=cluster.rpro
        v=cluster.vpro
    else:
        r=cluster.r
        v=cluster.v

    if rmin==None: rmin=np.min(r)
    if rmax==None: rmax=np.max(r)
    if vmin==None: vmin=np.min(v)
    if vmax==None: vmax=np.max(v)
    if mmin==None: mmin=np.min(cluster.m)
    if mmax==None: mmax=np.max(cluster.m)

    if indx==None:
        indx=(cluster.id > -1)

    #Build subcluster containing only stars in the full radial and mass range:
    indx*=(r >= rmin) * (r<=rmax) * (cluster.m >= mmin) * (cluster.m <= mmax) * (v >=vmin) * (v <=vmax) * (cluster.kw >=kwmin) * (cluster.kw <=kwmax)
  
    if emin!=None:
        indx*=(cluster.etot >= emin)
    if emin!=None:
        indx*=(cluster.etot <= emax)

    r_lower,r_mean,r_upper,r_hist=nbinmaker(cluster.r[indx],nrad)

    for i in range(0,len(r_mean)):
        m_mean,sigvm,eta,eeta,yeta,eyeta=eta_function(cluster,mmin=mmin,mmax=mmax,nmass=nmass,rmin=r_lower[i],rmax=r_upper[i],vmin=vmin,vmax=vmax,kwmin=kwmin,kwmax=kwmax,projected=projected,obs_cut=obs_cut)

        if alpha > -100:
            if projected:
                lrprofn.append(np.log(r_mean[i]/cluster.rmpro))
            else:
                lrprofn.append(np.log(r_mean[i]/cluster.rm))

            eprof.append(eta)

    if len(lrprofn)>3:
        (deta,ydeta),V=np.polyfit(lrprofn,eprof,1,cov=True)
        edeta=np.sqrt(V[0][0])
        eydeta=np.sqrt(V[1][1])
    else:
        deta=-100.0
        ydeta=0.0
        edeta=0.0
        eydeta=0.0

    return_cluster(cluster,units0,origin0,center0)

    return lrprofn,eprof,deta,edeta,ydeta,eydeta

