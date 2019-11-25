import os

from shared_astro_utils import astropy_utils

from decals.a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog
# duplicates existing start of upload_decals, but useful for lower-memory devices that can't do this and load the joint catalog

if __name__ == '__main__':

    nsa_loc = '/media/mike/beta/decals/catalogs/nsa_v1_0_0.fits'
    nsa_version = 'v1_0_0'
    cache_loc = '/media/mike/beta/decals/catalogs/nsa_v1_0_0_cached_for_upload.fits'
    assert not os.path.isfile(cache_loc)
    useful_cols = [
        'nsa_id',
        'iauname',
        'ra',
        'dec',
        'petroth50',
        'petrotheta',
        'petroflux',
        'nsa_version',
        'z',
        'mag',
        'absmag',
        'nmgy',
    ]

    astropy_utils.cache_table(nsa_loc, cache_loc, useful_cols, get_nsa_catalog, kwargs={'nsa_version': nsa_version})