""""
Make metadata table for DECaLS images
Using NSA and DECALS catalogs (matched previously), derive
a) astrometrics e.g. absolute size, magnitude by band (expanded from catalog)
b) galaxy zoo metadata e.g. url location, 'retire_at'

Runs on the 'goodimgs' catalog output after matching catalogs and downloading/checking fits
Equivalent to make_decals_metadata but for dr2. Minor changes to account for different data table.
"""""

import os
import logging

import numpy as np
from astropy import units as u
from astropy.cosmology import WMAP9  # IDE may show WMAP9 as 'not found'
from astropy.io import fits
from astropy.table import Table


def get_key_astrophysical_columns(catalog):
    """
    Select or calculate the most important astrophysical columns from the joint catalog
    This is useful to include in the 'metadata' portion of the subject upload
    Args:
        catalog (astropy.Table): joint catalog of decals subjects, with all columns

    Returns:
        (astropy.Table) The most important astrophysical values from the joint catalog
    """
    key_data = Table()

    columns_to_copy = [
        'iauname',
        'ra',
        'dec',
        'nsa_id',
        'petroth50',
        'petrotheta',
        'nsa_version'
    ]

    for col in columns_to_copy:
        try:
            key_data[col] = catalog[col]
        except KeyError:
            logging.critical('Key metadata column "{}" missing; manifest incomplete'.format(col), UserWarning)

    size = calculate_sizes_in_kpc(catalog)
    key_data['absolute_size'] = size.value

    mag = get_extinction_corrected_magnitudes(catalog)
    key_data['mag_faruv'] = mag[:, 0]
    key_data['mag_nearuv'] = mag[:, 1]
    key_data['mag_u'] = mag[:, 2]
    key_data['mag_g'] = mag[:, 3]
    key_data['mag_r'] = mag[:, 4]
    key_data['mag_i'] = mag[:, 5]
    key_data['mag_z'] = mag[:, 6]

    absmag_r = get_r_magnitude(catalog)
    key_data['mag_abs_r'] = absmag_r

    # TODO this column has gone missing somewhere
    # only works for DR5 catalog - but that's okay, we only need the latest
    # t['metadata.nexp_g'] = nsa_decals['nexp_g']
    # t['metadata.nexp_r'] = nsa_decals['nexp_r']
    # t['metadata.nexp_i'] = nsa_decals['nexp_i']

    fluxarr = get_r_flux(catalog)
    key_data['petroflux'] = fluxarr

    key_data['redshift'] = catalog['z']

    return key_data


def get_r_magnitude(catalog):
    # Calculate absolute and apparent magnitude
    # absmag is absolute magnitude estimates for FNugriz from K-corrections (Ωm=0.3, ΩΛ=0.7, h=1), 4th value is r-band
    absmag_r = catalog['absmag'][:, 4].astype(float)
    return absmag_r


def get_extinction_corrected_magnitudes(catalog):
    # nmgy: Galactic - extinction corrected AB flux used for K - correction(from SERSICFLUX) in FNugriz, in nanomaggies
    mag = 22.5 - 2.5 * np.log10(catalog['nmgy']).astype(float)
    return mag


def get_r_flux(catalog):
    # Azimuthally - averaged SDSS - style Petrosian flux in FNugriz
    fluxarr = catalog['petroflux'][:, 4].astype(float)
    return fluxarr


def calculate_sizes_in_kpc(catalog):
    size = WMAP9.kpc_proper_per_arcmin(catalog['z']).to(u.kpc/u.arcsec)*(catalog['petrotheta']*u.arcsec)
    size[catalog['z']<0] = -99.*u.kpc
    return size


if __name__ == '__main__':
    nsa_version = '1_0_0'
    # TODO currently only works for DR5
    data_release = '5'

    nsa_decals = Table(
        fits.getdata('/data/galaxy_zoo/decals/catalogs/nsa_v{}_decals_dr{}.fits'.format(nsa_version, data_release), 1))

    key_data = get_key_astrophysical_columns(nsa_decals)

    # Check format and content
    key_data[:5].show_in_browser()

    # Write to table
    ftypes = ('csv', 'fits')
    for filetype in ftypes:
        fname = '/data/galaxy_zoo/decals/catalogs/nsa_v{}_decals_dr{}_metadata.{}'.format(nsa_version, data_release,
                                                                                          filetype)
        if os.path.isfile(fname):
            os.remove(fname)
        key_data.write(fname)
