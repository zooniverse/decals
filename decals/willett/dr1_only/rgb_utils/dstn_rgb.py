gzpath = '/Users/willettk/Astronomy/Research/GalaxyZoo'

import os

import decals
import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt


def get_rgb(imgs, bands, mnmx=None, arcsinh=None, scales=None, imgname='test',desaturate=False):
    '''
    Given a list of images in the given bands, returns a scaled RGB
    image.

    *imgs*  a list of numpy arrays, all the same size, in nanomaggies
    *bands* a list of strings, eg, ['g','r','z']
    *mnmx*  = (min,max), values that will become black/white *after* scaling.
           Default is (-3,10)
    *arcsinh* use nonlinear scaling as in SDSS
    *scales*

    Returns a (H,W,3) numpy array with values between 0 and 1.
    '''
    bands = ''.join(bands)

    grzscales = dict(g = (2, 0.0066),
                      r = (1, 0.01385),
                      z = (0, 0.025),
                      )

    if scales is None:
        if bands == 'grz':
            scales = grzscales
        elif bands == 'urz':
            scales = dict(u = (2, 0.0066),
                          r = (1, 0.01),
                          z = (0, 0.025),
                          )
        elif bands == 'gri':
            # scales = dict(g = (2, 0.004),
            #               r = (1, 0.0066),
            #               i = (0, 0.01),
            #               )
            scales = dict(g = (2, 0.002),
                          r = (1, 0.004),
                          i = (0, 0.005),
                          )
        else:
            scales = grzscales
        
    h,w = imgs[0].shape
    rgb = np.zeros((h,w,3), np.float32)
    # Convert to ~ sigmas
    for im,band in zip(imgs, bands):
        plane,scale = scales[band]
        rgb[:,:,plane] = (im / scale).astype(np.float32)
        #print 'rgb: plane', plane, 'range', rgb[:,:,plane].min(), rgb[:,:,plane].max()

    if mnmx is None:
        mn,mx = -3, 10
    else:
        mn,mx = mnmx

    if arcsinh is not None:
        def nlmap(x):
            return np.arcsinh(x * arcsinh) / np.sqrt(arcsinh)
        rgb = nlmap(rgb)
        mn = nlmap(mn)
        mx = nlmap(mx)

    rgb = (rgb - mn) / (mx - mn)

    if desaturate:
        # optionally desaturate pixels that are dominated by a single
        # colour to avoid colourful speckled sky

        RGBim = np.array([rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]])
        a = RGBim.mean(axis=0)
        np.putmask(a, a == 0.0, 1.0)
        acube = np.resize(a,(3,h,w))
        bcube = (RGBim / acube) / 2.5
        mask = np.array(bcube)
        wt = np.max(mask,axis=0)
        np.putmask(wt, wt > 1.0, 1.0)
        wt = 1 - wt
        wt = np.sin(wt*np.pi/2.0)
        temp = RGBim * wt + a*(1-wt) + a*(1-wt)**2 * RGBim
        rgb = np.zeros((h,w,3), np.float32)
        for idx,im in enumerate((temp[0,:,:],temp[1,:,:],temp[2,:,:])):
            rgb[:,:,idx] = im

    clipped = np.clip(rgb, 0., 1.)

    # Save hardcopy as JPG
    #out_jpg  = '%s/decals/imagetests/dstn/test.jpeg'  % gzpath
    out_jpg  = '%s/decals/imagetests/sugata/%s.jpeg'  % (gzpath,imgname)

    plt.imsave(out_jpg, clipped, origin='lower')

    return clipped
    
if __name__ == "__main__":

    # Load FITS data from original DECaLS files

    '''
    galname = 'J103438.28-005109.6'

    with fits.open('%s/decals/imagetests/fits/%s_%s.fits' % (gzpath,galname,'z')) as f:
        img_z_cut = f[0].data
    '''

    # Try Sugata's examples of low-surface brightness galaxies

    galnames = ('J231817.76-010905.9', 'J225711.16-000815.9', 'J000000.80+004200.0')

    for galname in galnames:

        try:
            with fits.open('/Volumes/3TB/gz4/DECaLS/fits/nsa/%s_%s.fits' % (galname,'g')) as f:
                img_g_cut = f[0].data
            with fits.open('/Volumes/3TB/gz4/DECaLS/fits/nsa/%s_%s.fits' % (galname,'r')) as f:
                img_r_cut = f[0].data
            with fits.open('/Volumes/3TB/gz4/DECaLS/fits/nsa/%s_%s.fits' % (galname,'z')) as f:
                img_z_cut = f[0].data

            imgs = (img_g_cut,img_r_cut,img_z_cut)
            bands = 'grz'
            # Default settings from dstn: rgbkwargs = dict(mnmx=(-1,100.), arcsinh=1.)
            img = get_rgb(imgs, bands, mnmx=(-0.5,100.), arcsinh=1., scales=None,imgname=galname,desaturate=False)
            #os.system("open %s/decals/imagetests/dstn/test.jpeg"  % gzpath)
            os.system("open %s/decals/imagetests/sugata/%s.jpeg"  % (gzpath,galname))
        except IOError:
            print "Didn't find %s" % galname
            tempgals = decals.get_nsa_decals(highz=True)
            gal = tempgals[tempgals['IAUNAME'] == galname]
            decals.get_skyserver_fits(gal[0],fitspath='/Volumes/3TB/gz4/DECaLS/fits/nsa',remove_multi_fits=True)
