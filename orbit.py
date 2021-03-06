#Functions and Operations that focus on the cluster's orbit

from galpy.orbit import Orbit, Orbits
from galpy.util import bovy_coords,bovy_conversion
from galpy import potential
from galpy.potential import LogarithmicHaloPotential,MWPotential2014,rtide

import numpy as np

from recipes import rotate,interpolate
from operations import save_cluster,return_cluster
from profiles import rho_prof
from plots import *

def initialize_orbit(cluster,from_center=False,r0=8.,v0=220.):
 
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_galpy()

    if from_center:
       x,y,z=cluster.xgc+cluster.xc,cluster.ygc+cluster.yc,cluster.zgc+cluster.zc
       vx,vy,vz=cluster.vxgc+cluster.vxc,cluster.vygc+cluster.vyc,cluster.vzgc+cluster.vzc
    else:
        x,y,z=cluster.xgc,cluster.ygc,cluster.zgc
        vx,vy,vz=cluster.vxgc,cluster.vygc,cluster.vzgc

    R,phi,z=bovy_coords.rect_to_cyl(x,y,z)
    vR,vT,vz=bovy_coords.rect_to_cyl_vec(vx,vy,vz,x,y,z)
    o=Orbit([R,vR,vT,z,vz,phi],ro=r0,vo=v0,solarmotion=[-11.1,24.,7.25])

    cluster.orbit=o

    print(o.x(),o.y(),o.z())

    return_cluster(cluster,units0,origin0,center0)

    return o

def initialize_orbits(cluster,r0=8.,v0=220.):
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_galaxy()
    cluster.to_galpy()

    x,y,z=cluster.x,cluster.y,cluster.z
    vx,vy,vz=cluster.vx,cluster.vy,cluster.vz

    R,phi,z=bovy_coords.rect_to_cyl(x,y,z)
    vR,vT,vz=bovy_coords.rect_to_cyl_vec(vx,vy,vz,x,y,z)

    vxvv=np.array([R,vR,vT,z,vz,phi])
    vxvv=np.rot90(vxvv)
    os=Orbits(vxvv,ro=r0,vo=v0,solarmotion=[-11.1,24.,7.25])

    return_cluster(cluster,units0,origin0,center0)

    return os

def integrate_orbit(cluster,pot,tfinal=12.0,nt=1000,r0=8.,v0=220.,plot=False):
    cluster.orbit=initialize_orbit(cluster)
    ts=np.linspace(0,tfinal/bovy_conversion.time_in_Gyr(ro=r0,vo=v0),nt)
    cluster.orbit.integrate(ts,pot)

    if plot:
        cluster.orbit.plot()

    return ts,cluster.orbit

def orbit_interpolate(cluster,dt,pot,from_center=False,do_tails=False,rmin=None,rmax=None,emin=None,emax=None,r0=8.,v0=220.):
    cluster.tphys+=dt
    units0,origin0,center0=save_cluster(cluster)
    cluster.to_galaxy()
    
    if do_tails:
        
        cluster.to_cluster()
        if from_center:cluster.to_center()
        
        if rmin==None: rmin=np.min(cluster.r)
        if rmax==None: rmax=np.max(cluster.r)
        rindx=(cluster.r>=rmin) * (cluster.r<=rmax)
        
        if len(cluster.etot)==cluster.ntot:
            if emin==None: emin=np.min(cluster.etot)
            if emax==None: emax=np.max(cluster.etot)
            eindx=(cluster.etot>=emin) * (cluster.etot<=emax)
        else:
            eindx=cluster.id>-1
        
        indx=rindx * eindx
        tindx=np.invert(indx)
        
        cluster.to_galaxy()
    
    else:
        indx=cluster.id>-1
    
    print('DO CLUSTER')
    
    cluster.orbit=initialize_orbit(cluster,from_center)
    ts=np.linspace(0,dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0),10)
    print('INTEGRATE ORBIT')

    cluster.orbit.integrate(ts,pot)


    cluster.to_realkpc()

    if from_center:
        dx=cluster.orbit.x(ts[-1])-cluster.xc-cluster.xgc
        dy=cluster.orbit.y(ts[-1])-cluster.yc-cluster.ygc
        dz=cluster.orbit.z(ts[-1])-cluster.zc-cluster.zgc
        dvx=cluster.orbit.vx(ts[-1])-cluster.vxc-cluster.vxgc
        dvy=cluster.orbit.vy(ts[-1])-cluster.vyc-cluster.vygc
        dvz=cluster.orbit.vz(ts[-1])-cluster.vzc-cluster.vzgc
    else:
        dx=cluster.orbit.x(ts[-1])-cluster.xgc
        dy=cluster.orbit.y(ts[-1])-cluster.ygc
        dz=cluster.orbit.z(ts[-1])-cluster.zgc
        dvx=cluster.orbit.vx(ts[-1])-cluster.vxgc
        dvy=cluster.orbit.vy(ts[-1])-cluster.vygc
        dvz=cluster.orbit.vz(ts[-1])-cluster.vzgc
    
    print(dx,dy,dz,dvx,dvy,dvz)

    print('MOVING CLUSTER STARS')
    
    cluster.x[indx]+=dx
    cluster.y[indx]+=dy
    cluster.z[indx]+=dz
    cluster.vx[indx]+=dvx
    cluster.vy[indx]+=dvy
    cluster.vz[indx]+=dvz
    
    if from_center:
        cluster.xc,cluster.yc,cluster.zc=0.0,0.0,0.0
        cluster.vxc,cluster.vyc,cluster.vzc=0.0,0.0,0.0
    else:
        cluster.xc+=dx
        cluster.yc+=dy
        cluster.zc+=dz
        cluster.vxc+=dvx
        cluster.vyc+=dvy
        cluster.vzc+=dvz

    cluster.xgc,cluster.ygc,cluster.zgc=cluster.orbit.x(ts[-1]),cluster.orbit.y(ts[-1]),cluster.orbit.z(ts[-1])
    cluster.vxgc,cluster.vygc,cluster.vzgc=cluster.orbit.vx(ts[-1]),cluster.orbit.vy(ts[-1]),cluster.orbit.vz(ts[-1])

    if do_tails:
        cluster.to_galaxy()
        cluster.to_galpy()

        x,y,z=cluster.x[tindx],cluster.y[tindx],cluster.z[tindx]
        vx,vy,vz=cluster.vx[tindx],cluster.vy[tindx],cluster.vz[tindx]

        R,phi,z=bovy_coords.rect_to_cyl(x,y,z)
        vR,vT,vz=bovy_coords.rect_to_cyl_vec(vx,vy,vz,x,y,z)

        vxvv=np.array([R,vR,vT,z,vz,phi])
        vxvv=np.rot90(vxvv)
        otail=Orbits(vxvv,ro=r0,vo=v0,solarmotion=[-11.1,24.,7.25])

        cluster.to_realkpc()

        ts=np.linspace(0,dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0),10)

        print('INTEGRATE ORBITS')

        otail.integrate(ts,pot)
        
        print('MOVING TAIL STARS')

        cluster.x[tindx]=np.array(otail.x(ts[-1]))
        cluster.y[tindx]=np.array(otail.y(ts[-1]))
        cluster.z[tindx]=np.array(otail.z(ts[-1]))

        cluster.vx[tindx]=np.array(otail.vx(ts[-1]))
        cluster.vy[tindx]=np.array(otail.vy(ts[-1]))
        cluster.vz[tindx]=np.array(otail.vz(ts[-1]))

    return_cluster(cluster,units0,origin0,center0)


def orbital_path(cluster,dt=0.1,nt=100,pot=MWPotential2014,from_center=False,r0=8.,v0=220.):

    o=initialize_orbit(cluster,from_center=from_center)

    ts=np.linspace(0,-1.*dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0),nt)
    o.integrate(ts,pot)

    R,phi,z=bovy_coords.rect_to_cyl(o.x(ts[-1]),o.y(ts[-1]),o.z(ts[-1]))
    vR,vT,vz=bovy_coords.rect_to_cyl_vec(o.vx(ts[-1]),o.vy(ts[-1]),o.vz(ts[-1]),o.x(ts[-1]),o.y(ts[-1]),o.z(ts[-1]))
    o=Orbit([R/r0,vR/v0,vT/v0,z/r0,vz/v0,phi],ro=r0,vo=v0,solarmotion=[-11.1,24.,7.25])
    ts=np.linspace(0,2.*dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0),2.*nt)
    o.integrate(ts,pot)

    x=np.array(o.x(ts))
    y=np.array(o.y(ts))
    z=np.array(o.z(ts))
    vx=np.array(o.vx(ts))
    vy=np.array(o.vy(ts))
    vz=np.array(o.vz(ts))

    if cluster.units=='realpc':
        x*=1000.
        y*=1000.
        z*=1000.
        t=ts*bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
    elif cluster.units=='nbody':
        x*=(1000./cluster.rbar)
        y*=(1000./cluster.rbar)
        z*=(1000./luster.rbar)
        vx/=cluster.vstar
        vy/=cluster.vstar
        vz/=cluster.vstar
        t=ts*bovy_conversion.time_in_Gyr(ro=r0,vo=v0)/cluster.tstar

    elif cluster.units=='galpy':
        x/=r0
        y/=r0
        z/=r0
        vx/=v0 
        vy/=v0
        vz/=v0
        t=ts
    else:
        t=ts*bovy_conversion.time_in_Gyr(ro=r0,vo=v0)

    return t,x,y,z,vx,vy,vz,o

def orbital_path_match(cluster,dt=0.1,nt=100,pot=MWPotential2014,from_center=False,r0=8.,v0=220.):

    units0,origin0,center0=save_cluster(cluster)
    cluster.to_galaxy()
    cluster.to_realkpc()

    t,x,y,z,vx,vy,vz,o=orbital_path(cluster,dt=dt,nt=nt,pot=pot,from_center=False,r0=8.,v0=220.)

    ts=np.linspace(t[0],t[-1],10*nt)/bovy_conversion.time_in_Gyr(ro=r0,vo=v0)

    dx=np.tile(np.array(o.x(ts)),cluster.ntot).reshape(cluster.ntot,len(ts))-np.repeat(cluster.x,len(ts)).reshape(cluster.ntot,len(ts))
    dy=np.tile(np.array(o.y(ts)),cluster.ntot).reshape(cluster.ntot,len(ts))-np.repeat(cluster.y,len(ts)).reshape(cluster.ntot,len(ts))
    dz=np.tile(np.array(o.z(ts)),cluster.ntot).reshape(cluster.ntot,len(ts))-np.repeat(cluster.z,len(ts)).reshape(cluster.ntot,len(ts))
    dr=np.sqrt(dx**2.+dy**2.+dz**2.)
    
    indx=np.argmin(dr,axis=1)
    dpath=np.min(dr,axis=1)
    tstar=ts[indx]*bovy_conversion.time_in_Gyr(ro=r0,vo=v0)

    #Assign negative to stars with position vectors in opposite direction as local angular momentum vector
    rgc=np.column_stack([o.x(ts[indx]),o.y(ts[indx]),o.z(ts[indx])])
    vgc=np.column_stack([o.vx(ts[indx]),o.vy(ts[indx]),o.vz(ts[indx])])
    lz=np.cross(rgc,vgc)

    rstar=np.column_stack([cluster.x-o.x(ts[indx]),cluster.y-o.y(ts[indx]),cluster.z-o.z(ts[indx])])

    ldot=np.sum(rstar*lz,axis=1)
    dpath[ldot<0]*=-1 

    return_cluster(cluster,units0,origin0,center0)


    return np.array(tstar),np.array(dpath),o

def orbital_distance(cluster,dt=0.1,nt=100,pot=MWPotential2014,from_center=False,r0=8.,v0=220.):

    tstar,dpath,o=orbital_path_match(cluster,dt=dt,nt=nt,pot=pot,from_center=from_center,r0=r0,v0=v0)
    ts=tstar/bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
    torbit=dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
    
    #ds=int_t1^t2 sqrt((dx/dt)^2+(dy/dy)^2+(dz/dt)^2)
    dprog=[]
    for i in range(0,cluster.ntot):
        if tstar[i] < torbit:
            tint=np.linspace(ts[i],torbit,nt)
            ds=np.sqrt(o.vx(tint)**2.+o.vy(tint)**2.+o.vz(tint)**2.)
            tint*=bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
            dprog.append(-1.*np.trapz(ds,tint))
        else:
            tint=np.linspace(torbit,ts[i],nt)
            ds=np.sqrt(o.vx(tint)**2.+o.vy(tint)**2.+o.vz(tint)**2.)
            tint*=bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
            dprog.append(np.trapz(ds,tint))

    return tstar,dprog,dpath

def orbital_phase(cluster,dt=0.1,nt=100,pot=MWPotential2014,from_center=False,r0=8.,v0=220.):

    tstar,dpath,o=orbital_path_match(cluster,dt=dt,nt=nt,pot=pot,from_center=from_center,r0=r0,v0=v0)
    
    ts=tstar/bovy_conversion.time_in_Gyr(ro=r0,vo=v0)
    torbit=dt/bovy_conversion.time_in_Gyr(ro=r0,vo=v0)

    rnorm=np.sqrt(o.x(ts)**2.+o.y(ts)**2.+o.z(ts)**2.)
    r=np.column_stack([o.x(ts)/rnorm,o.y(ts)/rnorm,o.z(ts)/rnorm])

    rnorm=np.sqrt(cluster.xgc**2.+cluster.ygc**2.+cluster.zgc**2.)
    rgc=np.array([cluster.xgc/rnorm,cluster.ygc/rnorm,cluster.zgc/rnorm])

    phi=np.arccos(np.dot(r,rgc))

    indx=(ts < torbit)
    phi[indx]*=-1.

    return phi


 
def rtidal(cluster,pot=MWPotential2014 ,rtiterate=0,rgc=None,r0=8.,v0=220.):
    
    units0,origin0,center0=save_cluster(cluster)

    cluster.to_center()
    cluster.to_galpy()

    if rgc!=None:
        R=rgc/r0
        z=0.0
    else:
        R=np.sqrt(cluster.xgc**2.0+cluster.ygc**2.0)
        z=cluster.zgc

    #Calculate rtide
    rt=rtide(pot,R,z,M=cluster.mtot)
    nit=0
    for i in range(0,rtiterate):
        msum=0.0
        
        indx=(cluster.r < rt)
        msum=np.sum(cluster.m[indx])

        rtnew=rtide(pot,R,z,M=msum)
        
        print(rt,rtnew,rtnew/rt,msum/cluster.mtot)

        if rtnew/rt>=0.9:
            break
        rt=rtnew
        nit+=1

    print('FINAL RT: ',rt*r0*1000.0, 'pc after',nit,' of ',rtiterate,' iterations')

    if units0=='realpc':
        rt*=1000.0*r0
    elif units0=='realkpc':
        rt*=r0
    elif units0=='nbody':
        rt*=(1000.0*r0/cluster.rbar)

    cluster.rt=rt

    return_cluster(cluster,units0,origin0,center0)

    return rt

def rlimiting(cluster,pot=MWPotential2014 ,rgc=None,r0=8.,v0=220.,nrad=20,projected=False,obs_cut=False,plot=False,**kwargs):

    units0,origin0,center0=save_cluster(cluster)

    cluster.to_center()
    cluster.to_galpy()

    if rgc!=None:
        R=rgc/r0
        z=0.0
    else:
        R=np.sqrt(cluster.xgc**2.0+cluster.ygc**2.0)
        z=cluster.zgc

    #Calculate local density:
    rho_local=potential.evaluateDensities(pot,R,z,ro=r0,vo=v0)/bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)

    rprof,pprof,nprof=rho_prof(cluster,nrad=nrad,projected=projected,obs_cut=obs_cut)

    if pprof[-1] > rho_local:
        rl=rprof[-1]
    else:
        indx=np.argwhere(pprof < rho_local)[0][0]
        r1=(rprof[indx-1],pprof[indx-1])
        r2=(rprof[indx],pprof[indx])

        rl=interpolate(r1,r2,y=rho_local)

    print('FINAL RL: ',rl*r0*1000.0, 'pc')

    if units0=='realpc':
        rl*=1000.0*r0
    elif units0=='realkpc':
        rl*=r0
    elif units=='nbody':
        rl*=(1000.0*r0/cluster.rbar)

    cluster.rl=rl

    return_cluster(cluster,units0,origin0,center0)


    if plot:
        print('LOCAL DENSITY = ',rho_local)    

        filename=kwargs.pop('filename',None)   
        overplot=kwargs.pop('overplot',False)        
     
        if cluster.units=='nbody':
            rprof*=(r0*1000.0/cluster.rbar)
            pprof*=(bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)*(cluster.rbar**3.)/cluster.zmbar)
            rho_local*=(bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)*(cluster.rbar**3.)/cluster.zmbar)
            xunits=' (NBODY)'
            yunits=' (NBODY)'
        elif cluster.units=='realpc':
            rprof*=(r0*1000.0)
            pprof*=bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)
            rho_local*=bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)
            xunits=' (pc)'
            if projected:
                yunits=' Msun/pc^2'
            else:
                yunits=' Msun/pc^3'
        elif cluster.units=='realkpc':
            rprof*=r0
            pprof*=bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)*(1000.0**3.)
            rho_local*=bovy_conversion.dens_in_msolpc3(ro=r0,vo=v0)*(1000.0**3.)

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
        nlplot(x,np.ones(len(x))*rho_local,'--',overplot=True)
        nlplot(np.ones(len(y))*rl,y,'--',overplot=True)

        if filename!=None:
            plt.savefig(filename)

    return rl
