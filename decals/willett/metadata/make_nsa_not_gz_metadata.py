# Make metadata table for DECaLS images
# Using NSA and DECALS catalogs (matched previously), derive
# a) astrometrics e.g. absolute size, magnitude by band (expanded from catalog)
# b) galaxy zoo metadata e.g. url location, 'retire_at'


# Runs on the 'goodimgs' catalog output after matching catalogs and downloading/checking fits

# 'not_gz': these are galaxies which are part of the sdss lost set (and actually are now in gz)
# Not yet clear how to find which galaxies these are - what makes the data file?

import os
import warnings

import numpy as np
from astropy import units as u
from astropy.cosmology import WMAP9
from astropy.io import fits
from astropy.table import Table

warnings.simplefilter("ignore", RuntimeWarning)

version = '0_1_2'
nsa_not_gz = fits.getdata('../fits/nsa_v{0}_not_in_GZ_all_in_one.fits'.format(version), 1)

N = len(nsa_not_gz)

t = Table()

t['coords.0'] = nsa_not_gz['RA']
t['coords.1'] = nsa_not_gz['DEC']

# Calculate absolute size in kpc

size = WMAP9.kpc_proper_per_arcmin(nsa_not_gz['Z']).to(u.kpc/u.arcsec)*(nsa_not_gz['PETROTHETA']*u.arcsec)
size[nsa_not_gz['Z']<0] = -99.*u.kpc

# Calculate absolute and apparent magnitude

absmag_r = nsa_not_gz['ABSMAG'][:, 4].astype(float)
mag = 22.5 - 2.5*np.log10(nsa_not_gz['NMGY']).astype(float)
mag[~np.isfinite(mag)] = -99.

fluxarr = nsa_not_gz['PETROFLUX'][:, 4].astype(float)

url_stub = "http://www.galaxyzoo.org.s3.amazonaws.com/subjects/sdss_lost_set"

for imgtype in ('standard', 'inverted', 'thumbnail'):
    lst = url_stub + '/{0}/'.format(imgtype) + nsa_not_gz['IAUNAME'] + '.jpeg'
    t['location.{0}'.format(imgtype)] = lst

t['nsa_id'] = np.char.add('NSA_', nsa_not_gz['NSAID'].astype(str))

t['metadata.absolute_size'] = size.value
t['metadata.counters.feature'] = np.zeros(N, dtype=int)
t['metadata.counters.smooth'] = np.zeros(N, dtype=int)
t['metadata.counters.star'] = np.zeros(N, dtype=int)

t['metadata.mag.faruv'] = mag[:, 0]
t['metadata.mag.nearuv'] = mag[:, 1]
t['metadata.mag.u'] = mag[:, 2]
t['metadata.mag.g'] = mag[:, 3]
t['metadata.mag.r'] = mag[:, 4]
t['metadata.mag.i'] = mag[:, 5]
t['metadata.mag.z'] = mag[:, 6]
t['metadata.mag.abs_r'] = absmag_r

t['metadata.petrorad_50_r'] = nsa_not_gz['PETROTH50']
t['metadata.petroflux_r'] = fluxarr
t['metadata.petrorad_r'] = nsa_not_gz['PETROTHETA']
t['metadata.redshift'] = nsa_not_gz['Z']
t['metadata.retire_at'] = [40] * N
t['survey'] = ['decals'] * N

# Check format and content
#t[:5].show_in_browser()

# Write to table
ftypes = ('csv', 'fits')
for ft in ftypes:
    fname = '../fits/nsa_not_gz_metadata.{0}'.format(ft)
    if os.path.isfile(fname):
        os.remove(fname)
    t.write(fname)
