# Find entries in the NASA-Sloan Atlas (NSA) that have a brick with images in Dark Energy Camera Legacy Survey (DECaLS)

from __future__ import division

import datetime
import os
import random
import shutil
import urllib
from copy import deepcopy

import numpy as np
import nw
import requests
import trilogy
from PIL import Image
from StringIO import StringIO
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt

gzpath = '/Users/willettk/Astronomy/Research/GalaxyZoo'
min_pixelscale = 0.10

def get_nsa_images(highz=True):

    # Should be 145,155 galaxies (as of 26 May 2015)

    if highz:
        version = '1_0_0'
    else:
        version = '0_1_2'

    data = fits.getdata('%s/decals/nsa_v%s.fits' % (gzpath,version),1)

    return data

def get_decals_bricks():

    # Pre-sorted in TOPCAT to only include bricks with:
    #   images in r,g, and z bands
    #   bricks with a catalog entry
    #
    # Reduces the catalog from 662,174 to 13,769 (DR1 for DECaLS)

    data = fits.getdata('%s/decals/decals_allimages.fits' % gzpath,1)

    return data

def find_matching_brick(gal,bricks):

    # Bricks are roughly 0.25 deg x 0.25 deg on each side
    # Three sets of coordinates:
    # ra,dec = center of brick
    # ra1,dec1 = lower right corner of brick
    # ra2,dec2 = upper left corner of brick

    # Find only bricks that could match in RA,dec
    ragal,decgal = gal['RA'],gal['DEC']

    radiff_max = 0.30
    decdiff_max = 0.25

    ramatch = (bricks['ra1'] < ragal) & (bricks['ra2'] >= ragal)
    decmatch = (bricks['dec1'] < decgal) & (bricks['dec2'] >= decgal)

    coomatch = (ramatch & decmatch)
    nmatch = sum(coomatch)

    # Should only be 1 brick per galaxy max, but check
    '''
    if nmatch > 1:
        print 'Attention: %i matches for NSA %s (%.3f,%.3f)' % (nmatch,gal['IAUNAME'],ragal,decgal)
        for idx,brick in enumerate(bricks[coomatch]):
            print '\tBrick #%i: RA from %.3f to %.3f, dec from %.3f to %.3f' % (idx,brick['ra1'],brick['ra2'],brick['dec1'],brick['dec2'])
    '''

    return nmatch,coomatch

def run_all_bricks(nsa,bricks):

    # Make this somewhat quicker by eliminating everything outside the RA/dec range of bricks. Goes from 145K to 47K.

    brick_maxdec = max(bricks['dec2'])
    brick_mindec = min(bricks['dec1'])

    # Rough limits of DR1 in RA
    # Three blocks:
    #   7h to 11h
    #   21h to 1h
    #   15h to 18h

    ralim = ((nsa['RA'] > 15/24. * 360) & (nsa['RA'] < 18/24. * 360)) | (nsa['RA'] < 1/24. * 360) | (nsa['RA'] > 21/24. * 360) | (nsa['RA'] > 7/24. * 360) & (nsa['RA'] < 11/24. * 360)
    declim = (nsa['DEC'] >= brick_mindec) & (nsa['DEC'] <= brick_maxdec)

    total_matches = 0
    multi_matches = 0
    decals_indices = np.zeros(len(nsa),dtype=bool)
    bricks_indices = []

    endind = -1

    for idx,gal in enumerate(nsa[:endind]):
        if (declim & ralim)[idx]:
            nm,coomatch = find_matching_brick(gal,bricks)
            if nm > 0:
                total_matches += 1
                decals_indices[idx] = True
                bricks_indices.append(coomatch.argmax())
            if nm > 1:
                multi_matches += 1
        if idx % 100 == 0:
            print '%i galaxies searched, %i matches so far' % (idx,total_matches)

    print '%i total matches between NASA-Sloan Atlas and DECaLS DR1' % total_matches
    print '%i galaxies had matches in more than one brick' % multi_matches

    nsa_table = Table(nsa)
    nsa_decals = nsa_table[decals_indices]

    assert len(nsa_decals) == len(bricks_indices), \
        "Length of joint_catalog (%i) and bricks_indices (%i) must match" % (len(nsa_decals),len(bricks_indices))

    for bc in bricks.columns:
        nsa_decals[bc.name] = np.array(len(nsa_decals),dtype=bricks[bc.name].dtype)
        for ii in range(len(nsa_decals)):
            nsa_decals[ii][bc.name] = bricks[bricks_indices[ii]][bc.name]

    # Write to file

    # Check what version of the NSA is being used and set string variable below
    version = '1_0_0'
    nsa_decals.write('%s/decals/nsa_decals_v%s.fits' % (gzpath,version))

    return None

def get_nsa_decals(highz=True):

    version = '1_0_0' if highz else '0_1_2'

    nsa_decals = fits.getdata('%s/decals/nsa_decals_v%s.fits' % (gzpath,version),1)

    return nsa_decals

def plot_hists(highz=True):

    nsa = get_nsa_images(highz)

    if highz:
        version = '1_0_0'
        zlim = 0.15
    else:
        version = '0_1_2'
        zlim = 0.06

    nsa_decals = fits.getdata('%s/decals/nsa_decals_v%s.fits' % (gzpath,version),1)

    fig = plt.figure(figsize=(12,6))

    # Note - this is B-band magnitude, not r. 
    ax1 = fig.add_subplot(121)
    ax1.hist(nsa['MAG'],range=(10,25),bins=50,histtype='step',color='k',label='All NSA galaxies')
    ax1.hist(nsa_decals['MAG'],bins=20,histtype='stepfilled',label='NSA/DECaLS matches')
    ax1.set_xlabel(r'$m_r$ [mag]')
    ax1.set_ylabel('Count')

    ax2 = fig.add_subplot(122)
    ax2.hist(nsa['Z'],range=(0,zlim),bins=50,histtype='step',color='k',label='All NSA galaxies (%i)' % len(nsa))
    ax2.hist(nsa_decals['Z'],range=(0,zlim),bins=20,histtype='stepfilled',label='NSA/DECaLS matches (%i)' % len(nsa_decals))
    ax2.set_xlabel(r'$z$')
    ax2.set_ylabel('Count')
    ax2.legend(loc='upper left',fontsize=10)

    plt.savefig('%s/decals/nsa_decals_hist_v%s.pdf' % (gzpath,version))

    return None

def get_tractor(brickname='0001m002'):

    tractorfile = '%s/decals/tractor-%s.fits' % (gzpath,brickname)

    # Download file from legacysurvey website if it doesn't already exist locally

    if os.path.exists(tractorfile) == False:
        urllib.urlretrieve("http://portal.nersc.gov/project/cosmo/data/legacysurvey/dr1/tractor/%s/tractor-%s.fits" % (brickname[:3],brickname), tractorfile)

    tractor = fits.getdata(tractorfile,1)

    return tractor


def tractor_cut(tractor, verbose=False):

    '''
    Dustin Lang, 5 Jun 2015
    
    I'd suggest cutting to brick_primary = 1, decam_anymask = 0, and decam_nobs >= 1 for array elements 1, 2, and 4 (decam_nobs is an array for bands ugrizY).
    '''
    
    brick_primary = tractor['brick_primary']
    anymask = [np.logical_not(np.bool(x[1]) | np.bool(x[2]) | np.bool(x[4])) for x in tractor['decam_anymask']]
    nobs = [np.bool(x[1]) & np.bool(x[2]) & np.bool(x[4]) for x in tractor['decam_nobs']]
    
    '''
    I'm not sure what a reasonable minimum size is, but I'd guess you're right with the 5"-10" range.
    '''
    
    sizelim_arcsec = 10.
    
    sizearr = [x['shapeExp_r'] if x['fracDev'] < 0.5 else x['shapeDev_r'] for x in tractor]
    #sizearr = [np.max((x['shapeExp_r'],x['shapeDev_r'])) for x in tractor]
    sizemask = np.array(sizearr) > sizelim_arcsec
    
    # Require a flux measurement in all bands?
    
    flux = [True if np.min(x[[1,2,4]]) > 0 else False for x in tractor['decam_flux']]
    
    # Type of object
    
    not_star = [True if x != 'PSF' else False for x in tractor['type']]
    
    # Combine all cuts
    
    cuts = brick_primary & np.array(anymask) & np.array(nobs) & sizemask & np.array(flux) & np.array(not_star)
    
    if verbose:
        print("\nbrick_primary: %i galaxies" % sum(brick_primary))
        print("anymask: %i galaxies" % sum(np.array(anymask)))
        print("nobs: %i galaxies" % sum(np.array(nobs)))
        print("sizemask: %i galaxies" % sum(brick_primary))
        print("flux: %i galaxies" % sum(np.array(flux)))
        print("notstar: %i galaxies" % sum(np.array(not_star)))

    print('\n%i objects in file; %i meet all cuts on image quality and size' % (len(tractor), cuts.sum()))
    
    # What's the average magnitude of these galaxies?
    
    rflux = [x[2] for x in tractor[cuts]['decam_flux']]
    rmag = 22.5 - 2.5*np.log10(np.array(rflux))
    print("\nAverage r-band magnitude is %.1f +- %.1f" % (np.mean(rmag), np.std(rmag)))
    
    cutdata = tractor[cuts]
    
    return cutdata

def imageserver_jpeg(ra=114.5970,dec=21.5681,pixscale=2.,size=424):

    # Should be able to use Dustin Lang's image server to get both FITS and JPG images for what we want. Check with him that they're coadded?

    baseurl = "http://imagine.legacysurvey.org/jpeg-cutout-decals-dr1"
    params = {'ra':ra,'dec':dec,'pixscale':pixscale,'size':size}
    r = requests.get(baseurl,params)
    try:
        i = Image.open(StringIO(r.content))
        return i
    except IOError:
        print("IOError trying to download %s" % urllib.urlencode({'ra':ra,'dec':dec,'pixscale':pixscale,'size':size}))
        return None

def imageserver_fits(ra=114.5970,dec=21.5681,pixscale=2.,size=424):

    # Saves as default to file named `decals.fits'

    params = urllib.urlencode({'ra':ra,'dec':dec,'pixscale':pixscale,'size':size})
    url = "http://imagine.legacysurvey.org/fits-cutout-decals-dr1?%s" % params
    urllib.urlretrieve(url, "%s/decals/fits/%s.fits" % (gzpath,'decals'))

    return None

def check_fits_badpixels():

    # Download FITS images for the 100 random sample

    nsa_decals_full = fits.getdata('%s/decals/nsa_decals_v1_0_0.fits' % gzpath,0)
    N = 50
    galaxies = random.sample(nsa_decals_full,N)

    errcount = 0

    for gal in galaxies:
        ra,dec = gal['RA'],gal['DEC']
        pixscale = max(gal['PETROTH90']*0.02,min_pixelscale)
        params = urllib.urlencode({'ra':ra,'dec':dec,'pixscale':pixscale,'size':424})
        url = "http://imagine.legacysurvey.org/fits-cutout-decals-dr1?%s" % (params)
        urllib.urlretrieve(url, "%s/decals/fits/%s.fits" % (gzpath,"decals"))

    # Import into Python

        try:
            img,hdr = fits.getdata("%s/decals/fits/%s.fits" % (gzpath,"decals"),0,header=True)

            # Check to see what fraction have zero or NaN pixels

            badmax = 0.
            for i in range(img.shape[0]):
                band = img[i,:,:]
                nbad = (band == 0.).sum() + np.isnan(band).sum()
                total_pix = np.prod(band.shape)
                fracbad = nbad / total_pix

                #print "%.1f percent bad pixels for %s in band %s" % (fracbad*100,gal['IAUNAME'],hdr['BAND%i' % i])
                badmax = max(badmax,fracbad)

            print "Worst band in galaxy %s has %i percent bad pixels" % (gal['IAUNAME'],badmax*100)

            # 20% is a good cut on whether the image is suitable. 
            # Remaining issues:
            # - high noise levels & saturated colors at outer edges
            # - play with Trilogy and see if I can bring that down

            if badmax < 0.2:
                img = imageserver_jpeg(ra,dec,pixscale,424)
                img.show()

        except IOError:
            errcount += 1
            print "IOError for %s" % gal['IAUNAME']
        
    # Make HTML file?

    print "%i couldn't download FITS images" % errcount

    return None

def make_test_images(random_samp=False,public=False):

    nsa_decals = get_nsa_decals(highz=True)

    # Load examples from the NSA-DECaLS existing match

    N = 100
    if random_samp:
        galaxies = random.sample(nsa_decals,N)
    else:
        galaxies = nsa_decals[:N]

    badcount = 0

    f = open("%s/decals/decals_comparison.html" % gzpath,"w")

    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('  <meta charset=utf-8 />\n')
    f.write('  <title></title>\n')
    f.write('  <style>\n')
    f.write('    div.container {\n')
    f.write('      display:inline-block;\n')
    f.write('    }\n')
    f.write('\n')
    f.write('    p {\n')
    f.write('      text-align:center;\n')
    f.write('    }\n')
    f.write('  </style>\n')
    f.write('</head>\n')
    f.write('<body>\n')

    for idx,gal in enumerate(galaxies):
        ra,dec = gal['RA'],gal['DEC']
        pixscale = max(gal['PETROTH90']*0.02,min_pixelscale)

        # Do the FITS images exist?
        fits_filename_test = '%s/decals/imagetests/fits/%s.fits' % (gzpath,gal['IAUNAME'])
        if os.path.exists(fits_filename_test) == False:
            get_skyserver_fits(gal,fitspath='%s/decals/imagetests/fits' % gzpath,remove_multi_fits=False)

        # Check if FITS images are good in all bands

        try:
            img,hdr = fits.getdata(fits_filename_test,0,header=True)

            # Check to see what fraction have zero or NaN pixels

            badmax = 0.
            for i in range(img.shape[0]):
                band = img[i,:,:]
                nbad = (band == 0.).sum() + np.isnan(band).sum()
                total_pix = np.prod(band.shape)
                fracbad = nbad / total_pix

                #print "%.1f percent bad pixels for %s in band %s" % (fracbad*100,gal['IAUNAME'],hdr['BAND%i' % i])
                badmax = max(badmax,fracbad)

            firstgoodone = 0
            # 20% cut on whether the image is suitable. 
            if badmax < 0.2:

                # Does Skyserver JPEG image exist in test directory?
                jpeg_filename_test = '%s/decals/imagetests/jpeg_skyserver/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_test) == False:
                    jpeg_filename_main = '%s/decals/jpeg/nsa/%s.jpeg' % (gzpath,gal['IAUNAME'])
                    if os.path.exists(jpeg_filename_main) == False:
                        img = imageserver_jpeg(ra,dec,pixscale)
                    else:
                        shutil.copy(jpeg_filename_main,jpeg_filename_test)

                # Does the Trilogy JPEG image exist?
                jpeg_filename_trilogy = '%s/decals/imagetests/jpeg_trilogy/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_trilogy) == False:
                    trilogy_jpeg(gal['IAUNAME'])

                # Does the GZH JPEG image exist?
                jpeg_filename_gzh = '%s/decals/imagetests/jpeg_gzh/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_gzh) == False:
                    make_gzh_jpeg(gal['IAUNAME'],show_img=False)

                # Does the JPEG image made with Dustin's RGB technique exist?
                jpeg_filename_dstn = '%s/decals/imagetests/jpeg_dstn/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_dstn) == False:
                    rgb_img = dstn_rgb((img[0,:,:],img[1,:,:],img[2,:,:]), 'grz', mnmx=(-0.5,100.), arcsinh=1., scales=None, desaturate=True)
                    plt.imsave(jpeg_filename_dstn, rgb_img, origin='lower')

                # Add to HTML comparison page
                f.write('  <div class="container">\n')
                if public:
                    srcpath = "decals"
                    imsize = 300
                else:
                    srcpath = "/Users/willettk/Astronomy/Research/GalaxyZoo/decals/imagetests/jpeg_gzh"
                    imsize = 424

                if not firstgoodone:
                    f.write('    <p> v1 (KWW manual) </p>\n')
                f.write('    <img class="left-img" src="%s/jpeg_gzh/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v1.5 (modified DECaLS skyserver) </p>\n')
                f.write('    <img class="middle-img" src="%s/jpeg_dstn/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v2 (DECaLS skyserver) </p>\n')
                f.write('    <img class="middle-img" src="%s/jpeg_skyserver/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v3 (Trilogy manual) </p>\n')
                f.write('    <img class="right-img" src="%s/jpeg_trilogy/%s.png" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('<br>\n')

                firstgoodone += 1

            else:
                #print "Bad band(s) for %s" % gal['IAUNAME']
                badcount += 1

        except IOError:
            print "IOError for %s" % gal['IAUNAME']
 
        if not idx % 10:
            print idx

    f.write('</body>\n')
    f.write('</html>\n')
    f.close()

    print "\n%i galaxies out of %i had bad imaging in one or more bands" % (badcount,N)

    # Make HTML page

    if public:
        os.system("rsync -avzh %s/decals/decals_comparison.html willett@lucifer1.spa.umn.edu:public_html/" % gzpath)

    return None

def get_skyserver_fits(gal,fitspath='%s/decals/fits/nsa' % gzpath,remove_multi_fits=True):

    # Get FITS

    galname = gal['IAUNAME']
    params = urllib.urlencode({'ra':gal['RA'],'dec':gal['DEC'],'pixscale':max(min(gal['PETROTH50']*0.04,gal['PETROTH90']*0.02),min_pixelscale),'size':424})
    url = "http://imagine.legacysurvey.org/fits-cutout-decals-dr1?%s" % (params)
    urllib.urlretrieve(url, "%s/%s.fits" % (fitspath,galname))

    # Write multi-plane FITS images to separate files for each band

    data,hdr = fits.getdata("%s/%s.fits" % (fitspath,galname),0,header=True)
    for idx,plane in enumerate('grz'):
        hdr_copy = hdr.copy()
        hdr_copy['NAXIS'] = 2
        hdr_copy['FILTER'] = '%s       ' % plane
        for badfield in ('BANDS','BAND0','BAND1','BAND2','NAXIS3'):
            hdr_copy.remove(badfield)
        fits.writeto("%s/%s_%s.fits" % (fitspath,galname,plane),data[idx,:,:],hdr_copy,clobber=True)


    if remove_multi_fits:
        os.remove("%s/%s.fits" % (fitspath,galname))
    del data,hdr

    return None

def trilogy_jpeg(galname="J000123.73-005106.9",noiselum=0.15,samplesize=200):

    # Set the Trilogy parameters explicitly for a multi-plane FITS image

    # Create input file for Trilogy

    infile = "%s/decals/imagetests/trilogy.in" % gzpath
    with open(infile,"w") as f:
        f.write("B\n")
        f.write("%s_g.fits\n\n" % galname)
        f.write("G\n")
        f.write("%s_r.fits\n\n" % galname)
        f.write("R\n")
        f.write("%s_z.fits\n\n" % galname)
        f.write("indir %s/decals/imagetests/fits/\n" % gzpath) 
        f.write("outdir %s/decals/imagetests/\n" % gzpath) 
        f.write("outname %s/decals/imagetests/jpeg_trilogy/%s\n" % (gzpath,galname))
        f.write("noiselum %.2f\n" % noiselum)
        f.write("samplesize %i\n" % samplesize)
        f.write("sampledx 0\n")
        f.write("sampledy 0\n")
        f.write("show 0\n")
        f.write("verbose 0\n")
        f.write("legend 1\n")
        f.write("testfirst 0\n")

    trilogy.Trilogy(infile, images=None, **trilogy.params_cl()).run()

    return None
    
def get_image_defaults(color_scheme='grz'):

    # Used for make_gzh_jpeg

    ascales= 2.0*np.array([3.8, 6, 8])

    #ascales = 1.75 * np.array([20.,20.,20.])

    # according to Roger Griffith's program (also adapted from Hogg's)
    anonlinearity= 2.5
    
    # number of pixels the final image should have (in x and y, each)
    npix_final = 424

    # Pedestal
    apedestal = 0

    return ascales,anonlinearity,npix_final,apedestal

def make_gzh_jpeg(galname,color_scheme='grz',desaturate=True,show_img=True):

    ascales,anonlinearity,npix_final,apedestal = get_image_defaults(color_scheme=color_scheme)

    # Load FITS data from original DECaLS files

    with fits.open('%s/decals/imagetests/fits/%s_%s.fits' % (gzpath,galname,'g')) as f:
        img_g_cut = f[0].data
    with fits.open('%s/decals/imagetests/fits/%s_%s.fits' % (gzpath,galname,'r')) as f:
        img_r_cut = f[0].data
    with fits.open('%s/decals/imagetests/fits/%s_%s.fits' % (gzpath,galname,'z')) as f:
        img_z_cut = f[0].data

    # Check that all image sizes and shapes match
    # If all images don't exist, return assertion error

    assert img_g_cut.shape == img_r_cut.shape == img_z_cut.shape, \
        'Cutout images must be the same shape\n g:%s, r:%s, z:%s' % \
        (img_g_cut.shape,img_r_cut.shape,img_z_cut.shape)

    if color_scheme == 'grz':
        rimage = img_z_cut
        gimage = img_r_cut
        bimage = img_g_cut

    nx,ny = rimage.shape

    RGBim = np.array([rimage,gimage,bimage])
    
    # Use Nick Wherry's adapted IDL codes to scale and fit the image data
    RGBim = nw.scale_rgb(RGBim,scales=ascales)
    RGBim = nw.arcsinh_fit(RGBim,nonlinearity=anonlinearity)
    RGBim = nw.fit_to_box(RGBim)

    if desaturate:
        # optionally desaturate pixels that are dominated by a single
        # colour to avoid colourful speckled sky

        orig = deepcopy(RGBim)
        # Take the mean flux value between the three color bands
        a = RGBim.mean(axis=0)
        # mask pixels with no flux in any of the bands
        np.putmask(a, a == 0.0, 1.0)
        # create cube with each plane containing mean flux value
        acube = np.resize(a,(3,ny,nx))
        # scale each color to the mean, then divide by non-linearity factor
        bcube = (RGBim / acube) / anonlinearity
        # create a mask based on the weighted non-linear color values
        mask = np.array(bcube)
        # find the maximum weighted value per color
        w = np.max(mask,axis=0)
        # if the max value is greater than 1, replace with 1
        np.putmask(w, w > 1.0, 1.0)
        # invert mapping from 0 to 1.
        w = 1 - w
        # taper the weights with a sin function
        w = np.sin(w*np.pi/2.0)
        # multiply the original image by the normalized weights, add back the weighted mean flux, and [optionally] recolor strongest pixels
        #RGBim = RGBim * w + a*(1-w)
        RGBim = RGBim * w + a*(1-w) + a*(1-w)**2 * orig

    # Convert data to scaled bytes
    RGBim = (255.*RGBim).astype(int)
    RGBim = np.where(RGBim>255,255,RGBim)
    RGBim = np.where(RGBim<0,0,RGBim)

    # Add optional grey pedestal to the byte-scaled data

    RGBim += apedestal
    RGBim = np.where(RGBim>255,255,RGBim)

    R = RGBim[0,:,:]
    G = RGBim[1,:,:]
    B = RGBim[2,:,:]

    data = np.array([R.ravel(),G.ravel(),B.ravel()])
    data = np.transpose(data)
    pdata = []
    # putdata(x) does not work unless the (R,G,B) is given as tuple!!
    for each in data: 
        pdata.append(tuple(each))

    # Make Image in PIL format

    img = Image.new('RGB',size=R.shape)
    img.putdata(pdata)

    # Rebin images to 424x424 pixels
    img_resized = img.resize((424,424),Image.ANTIALIAS)

    # Reset orientation to match the native FITS (N up, E right)
    img_flipped = img_resized.transpose(Image.FLIP_TOP_BOTTOM)

    img_out = img_flipped

    if show_img:
        img_out.show()

    # Save hardcopy as JPG
    out_jpg  = '%s/decals/imagetests/jpeg_gzh/%s.jpeg'  % (gzpath,galname)
    img_out.save(out_jpg,format='JPEG',quality=100)

    return img,pdata

def dstn_rgb(imgs, bands, mnmx=None, arcsinh=None, scales=None, desaturate=False):

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

    return clipped
 
def run_tractor(cutdata):

    # Try this with a different brick

    for gal in cutdata:
        ra,dec = gal['ra'],gal['dec']
        pixscale = max(max(gal['shapeExp_r'] * 0.02,gal['shapeDev_r'] * 0.02),min_pixelscale)
        i = imageserver_jpeg(ra,dec,pixscale)
        i.save('%s/decals/jpeg/tractor/%s_%04i.jpeg' % (gzpath,gal['brickname'],gal['objid']),format='jpeg')

    return None

def tquick(brickname):

    tractor = get_tractor(brickname)
    cutdata = tractor_cut(tractor,verbose=True)
    run_tractor(cutdata)

    return None

def run_nsa(nsa_decals_full,random_samp=True,force_fits=False):

    if random_samp:
        N = 101
        galaxies = random.sample(nsa_decals_full,N)
    else:
        galaxies = nsa_decals_full

    # Set new parameters

    _scales = dict(g = (2, 0.008), r = (1, 0.014), z = (0, 0.019))
    _mnmx = (-0.5,300)

    for i,gal in enumerate(galaxies):

        # Check if FITS image already exists
        volpath = '/Volumes/3TB/gz4/DECaLS'
        fitspath = '%s/fits/nsa' % volpath
        fits_filename = '%s/%s.fits' % (fitspath,gal['IAUNAME'])
        if os.path.exists(fits_filename) == False:
            get_skyserver_fits(gal,fitspath,remove_multi_fits=False)

        if force_fits:
            # Force getting new images if coordinates, pixscale, or image size changes
            get_skyserver_fits(gal,fitspath,remove_multi_fits=False)

        # Check if new JPEG image already exists
        jpegpath = '%s/jpeg/nsa' % volpath
        jpeg_filename = '%s/%s.jpeg' % (jpegpath,gal['IAUNAME'])
        if os.path.exists(jpeg_filename) == False:
            try:
                img,hdr = fits.getdata(fits_filename,0,header=True)

                badmax = 0.
                for j in range(img.shape[0]):
                    band = img[j,:,:]
                    nbad = (band == 0.).sum() + np.isnan(band).sum()
                    fracbad = nbad / np.prod(band.shape)
                    badmax = max(badmax,fracbad)

                if badmax < 0.2:
                    rgbimg = dstn_rgb((img[0,:,:],img[1,:,:],img[2,:,:]), 'grz', mnmx=_mnmx, arcsinh=1., scales=_scales, desaturate=True)
                    plt.imsave(jpeg_filename, rgbimg, origin='lower')
            except IOError:
                print "Couldn't find image for %s" % fits_filename

        if not i % 10:
            print '%5i/%5i galaxies completed; %s' % (i,len(galaxies),datetime.datetime.now().strftime("%H:%M:%S"))

    return None

def test_images_etgs(public=False):

    galaxies = fits.getdata('%s/decals/stripe82_etgs_decals.fits' % gzpath,1)

    badcount = 0

    f = open("%s/decals/decals_etg_comparison.html" % gzpath,"w")

    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('  <meta charset=utf-8 />\n')
    f.write('  <title></title>\n')
    f.write('  <style>\n')
    f.write('    div.container {\n')
    f.write('      display:inline-block;\n')
    f.write('    }\n')
    f.write('\n')
    f.write('    p {\n')
    f.write('      text-align:center;\n')
    f.write('    }\n')
    f.write('  </style>\n')
    f.write('</head>\n')
    f.write('<body>\n')

    g,r,z = 0.008,0.014,0.019
    myscales = dict(g = (2, g), r = (1, r), z = (0, z))
    _min,_max = -0.5,300

    for idx,gal in enumerate(galaxies):
        ra,dec = gal['RA'],gal['DEC']
        pixscale = max(gal['PETROTH90']*0.02,min_pixelscale)

        # Do the FITS images exist?
        fits_filename_test = '%s/decals/imagetests/fits/%s.fits' % (gzpath,gal['IAUNAME'])
        if os.path.exists(fits_filename_test) == False:
            get_skyserver_fits(gal,fitspath='%s/decals/imagetests/fits' % gzpath,remove_multi_fits=False)

        # Check if FITS images are good in all bands

        try:
            img,hdr = fits.getdata(fits_filename_test,0,header=True)

            # Check to see what fraction have zero or NaN pixels

            badmax = 0.
            for i in range(img.shape[0]):
                band = img[i,:,:]
                nbad = (band == 0.).sum() + np.isnan(band).sum()
                total_pix = np.prod(band.shape)
                fracbad = nbad / total_pix

                badmax = max(badmax,fracbad)

            firstgoodone = 0
            # 20% cut on whether the image is suitable. 
            if badmax < 0.2:

                # Does Skyserver JPEG image exist in test directory?
                jpeg_filename_test = '%s/decals/imagetests/jpeg_skyserver/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_test) == False:
                    jpeg_filename_main = '%s/decals/jpeg/nsa/%s.jpeg' % (gzpath,gal['IAUNAME'])
                    if os.path.exists(jpeg_filename_main) == False:
                        img = imageserver_jpeg(ra,dec,pixscale)
                    else:
                        shutil.copy(jpeg_filename_main,jpeg_filename_test)

                # Does the Trilogy JPEG image exist?
                jpeg_filename_trilogy = '%s/decals/imagetests/jpeg_trilogy/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_trilogy) == False:
                    trilogy_jpeg(gal['IAUNAME'])

                # Does the GZH JPEG image exist?
                jpeg_filename_gzh = '%s/decals/imagetests/jpeg_gzh/%s.jpeg' % (gzpath,gal['IAUNAME'])
                if os.path.exists(jpeg_filename_gzh) == False:
                    make_gzh_jpeg(gal['IAUNAME'],show_img=False)

                # Does the JPEG image made with Dustin's RGB technique exist?
                jpeg_filename_dstn = '%s/decals/imagetests/jpeg_dstn/%s.jpeg' % (gzpath,gal['IAUNAME'])
                #if os.path.exists(jpeg_filename_dstn) == False:
                rgb_img = dstn_rgb((img[0,:,:],img[1,:,:],img[2,:,:]), 'grz', mnmx=(_min,_max), arcsinh=1., scales=myscales, desaturate=True)
                plt.imsave(jpeg_filename_dstn, rgb_img, origin='lower')

                # Add to HTML comparison page
                f.write('  <div class="container">\n')
                srcpath = "/Users/willettk/Astronomy/Research/GalaxyZoo/decals/imagetests"
                imsize = 300

                if not firstgoodone:
                    f.write('    <p> v1 (KWW manual) </p>\n')
                f.write('    <img class="left-img" src="%s/jpeg_gzh/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v1.5 (modified DECaLS skyserver) </p>\n')
                f.write('    <img class="middle-img" src="%s/jpeg_dstn/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v2 (DECaLS skyserver) </p>\n')
                f.write('    <img class="middle-img" src="%s/jpeg_skyserver/%s.jpeg" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('  <div class="container">\n')
                if not firstgoodone:
                    f.write('    <p> v3 (Trilogy manual) </p>\n')
                f.write('    <img class="right-img" src="%s/jpeg_trilogy/%s.png" height="%i" width="%i" />\n' % (srcpath,gal['IAUNAME'],imsize,imsize))
                f.write('  </div>\n')
                f.write('<br>\n')

                firstgoodone += 1

            else:
                #print "Bad band(s) for %s" % gal['IAUNAME']
                badcount += 1

        except IOError:
            print "IOError for %s" % gal['IAUNAME']
 
        if not idx % 10:
            print idx

    f.write('</body>\n')
    f.write('</html>\n')
    f.close()

    # Make HTML page

    if public:
        os.system("rsync -avzh %s/decals/decals_comparison.html willett@lucifer1.spa.umn.edu:public_html/" % gzpath)

    return None

def colortests():

    IAUNAME = "J230920.26+004523.3"

    IAUNAME = "J001233.70-000254.4"

    f = open("%s/decals/decals_colortests.html" % gzpath,"w")

    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('  <meta charset=utf-8 />\n')
    f.write('  <title></title>\n')
    f.write('  <style>\n')
    f.write('    div.container {\n')
    f.write('      display:inline-block;\n')
    f.write('    }\n')
    f.write('\n')
    f.write('    p {\n')
    f.write('      text-align:center;\n')
    f.write('    }\n')
    f.write('  </style>\n')
    f.write('</head>\n')
    f.write('<body>\n')

    # Do the FITS images exist?
    fits_filename_test = '%s/decals/imagetests/fits/%s.fits' % (gzpath,IAUNAME)
    if os.path.exists(fits_filename_test) == False:
        get_skyserver_fits(gal,fitspath='%s/decals/imagetests/fits' % gzpath,remove_multi_fits=False)

    img,hdr = fits.getdata(fits_filename_test,0,header=True)

    _g = 0.0066
    _r = 0.01385
    _z = 0.025

    garr = np.linspace(_g-_g/2.,_g+_g/2.,5)
    rarr = np.linspace(_r-_r/2.,_r+_r/2.,5)
    zarr = np.linspace(_z-_z/2.,_z+_z/2.,5)

    '''
    for g in garr:
        for r in rarr:
            for z in zarr:

                myscales = dict(g = (2, g), r = (1, r), z = (0, z))

                # Does the JPEG image made with Dustin's RGB technique exist?
                filename = "%s_%.3fg_%.3fr_%.3fz.jpeg" % (IAUNAME,g,r,z)
                jpeg_filename = '%s/decals/imagetests/colortests/%s' % (gzpath,filename)
                rgb_img = dr2_style_rgb((img[0,:,:],img[1,:,:],img[2,:,:]), 'grz', mnmx=(-0.5,100.), arcsinh=1., scales=myscales, desaturate=True)
                plt.imsave(jpeg_filename, rgb_img, origin='lower')

                # Add to HTML comparison page
                imsize = 250

                #f.write('    <p> %.2f %.2f %.2f </p>\n' % (g,r,z))
                f.write('    <img src="%s" height="%i" width="%i" title="%s"/>\n' % (jpeg_filename,imsize,imsize,jpeg_filename.split('/')[-1]))
    '''

    g,r,z = 0.008,0.014,0.019
    myscales = dict(g = (2, g), r = (1, r), z = (0, z))
    
    minarr = np.linspace(-2,0,15)
    maxarr = np.linspace(50,1000,5)
    for _min in minarr:
        for _max in maxarr:
            filename = "%s_min%.3f_max%.3f.jpg" % (IAUNAME,_min,_max)
            jpeg_filename = '%s/decals/imagetests/colortests/%s' % (gzpath,filename)
            rgb_img = dstn_rgb((img[0,:,:],img[1,:,:],img[2,:,:]), 'grz', mnmx=(_min,_max), arcsinh=1., scales=myscales, desaturate=True)
            plt.imsave(jpeg_filename, rgb_img, origin='lower')
            
            imsize = 250
            
            f.write('    <img src="%s" height="%i" width="%i" title="%s"/>\n' % (jpeg_filename,imsize,imsize,jpeg_filename.split('/')[-1]))

    f.write('</body>\n')
    f.write('</html>\n')
    f.close()

    # Make HTML page

    return None
