# Make metadata table for DECaLS images
# Using NSA and DECALS catalogs (matched previously), derive
# a) astrometrics e.g. absolute size, magnitude by band (expanded from catalog)
# b) galaxy zoo metadata e.g. url location, 'retire_at'

# Runs on the 'goodimgs' catalog output after matching catalogs and downloading/checking fits

import os
import warnings

import numpy as np
from astropy import units as u
from astropy.cosmology import WMAP9
from astropy.io import fits
from astropy.table import Table

warnings.simplefilter("ignore", RuntimeWarning)

gzpath = '/Users/willettk/Astronomy/Research/GalaxyZoo'

version = '1_0_0'
nsa_decals = fits.getdata('%s/decals/nsa_decals_v%s_goodimgs.fits' % (gzpath, version), 1)

N = len(nsa_decals)

t = Table()

t['coords.0'] = nsa_decals['RA']
t['coords.1'] = nsa_decals['DEC']

# Calculate absolute size in kpc
size = [WMAP9.kpc_proper_per_arcmin(z).to(u.kpc / u.arcsec) * (r * u.arcsec)
        if z > 0 else -99. * u.kpc for z, r in zip(nsa_decals['Z'], nsa_decals['PETROTHETA'])]

# Calculate absolute and apparent magnitude
absmag_r = [float(x[4]) for x in nsa_decals['ABSMAG']]
mag_faruv = [22.5 - 2.5*np.log10(x[0]) for x in nsa_decals['NMGY']]
mag_nearuv = [22.5 - 2.5*np.log10(x[1]) for x in nsa_decals['NMGY']]
mag_u = [22.5 - 2.5*np.log10(x[2]) for x in nsa_decals['NMGY']]
mag_g = [22.5 - 2.5*np.log10(x[3]) for x in nsa_decals['NMGY']]
mag_r = [22.5 - 2.5*np.log10(x[4]) for x in nsa_decals['NMGY']]
mag_i = [22.5 - 2.5*np.log10(x[5]) for x in nsa_decals['NMGY']]
mag_z = [22.5 - 2.5*np.log10(x[6]) for x in nsa_decals['NMGY']]

sizearr = [s.value for s in size]

fluxarr = [x[4] for x in nsa_decals['PETROFLUX']]

# record url location in galaxy zoo
url_stub = "http://www.galaxyzoo.org.s3.amazonaws.com/subjects/decals"

for imgtype in ('standard', 'inverted', 'thumbnail'):
    lst = ['%s/%s/%s_%s.jpg' % (url_stub, imgtype, s, imgtype) for s in nsa_decals['IAUNAME']]
    t['location.%s' % imgtype] = lst

t['nsa_id'] = ['NSA_%i' % x for x in nsa_decals['NSAID']]

t['metadata.absolute_size'] = sizearr
t['metadata.counters.feature'] = np.zeros(N, dtype=int)
t['metadata.counters.smooth'] = np.zeros(N, dtype=int)
t['metadata.counters.star'] = np.zeros(N, dtype=int)

t['metadata.mag.faruv'] = mag_faruv
t['metadata.mag.nearuv'] = mag_nearuv
t['metadata.mag.u'] = mag_u
t['metadata.mag.g'] = mag_g
t['metadata.mag.r'] = mag_r
t['metadata.mag.i'] = mag_i
t['metadata.mag.z'] = mag_z
t['metadata.mag.abs_r'] = absmag_r

t['metadata.nobs_max.g'] = nsa_decals['nobs_g_max']
t['metadata.nobs_max.r'] = nsa_decals['nobs_r_max']
t['metadata.nobs_max.z'] = nsa_decals['nobs_z_max']

t['metadata.petrorad_50_r'] = nsa_decals['PETROTH50']
t['metadata.petroflux_r'] = fluxarr
t['metadata.petrorad_r'] = nsa_decals['PETROTHETA']
t['metadata.redshift'] = nsa_decals['Z']
t['metadata.retire_at'] = [40] * N
t['survey'] = ['decals'] * N

# Check format and content
# t.show_in_browser()

# Write to table
ftypes = ('csv', 'fits')
for ft in ftypes:
    fname = '%s/decals/metadata/decals_metadata.%s' % (gzpath, ft)
    if os.path.isfile(fname):
        os.remove(fname)
    t.write(fname)
