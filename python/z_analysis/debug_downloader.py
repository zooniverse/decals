
from astropy.table import Table
from astropy.io import fits

from a_download_decals.get_images.download_images_threaded import download_images_multithreaded, get_fits_loc

# import pytest


# @pytest.fixture()
def fake_joint_catalog():

    # fits_dir = '/data/temp'
    # png_dir = '/data/temp'
    # TEST_EXAMPLES_DIR = '/data/temp'

    # fits_dir = '/home/walmsleym/temp_home'
    # png_dir = '/home/walmsleym/temp_home'
    # TEST_EXAMPLES_DIR = '/home/walmsleym/temp_home'

    fits_dir = '/home/mike/temp'
    png_dir = '/home/mike/temp'
    TEST_EXAMPLES_DIR = '/home/mike/temp'



    # TODO bad practice: fits_loc is overwritten in some tests
    gal_missing = {
        'iauname': 'J0',
        'fits_loc': '{}/example_missing.fits'.format(fits_dir),
        'png_loc': '{}/example_missing.png'.format(png_dir),
        'ra': 146.714208787,
        'dec': -1.04128156958,
        'petroth50': 3.46419,
        'petroth90': 10.4538}

    gal_incomplete = {
        'iauname': 'J1',
        'fits_loc': '{}/example_incomplete.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': '{}/example_incomplete.png'.format(TEST_EXAMPLES_DIR),
        'ra': 146.714208787,
        'dec': -1.04128156958,
        'petroth50': 3.46419,
        'petroth90': 10.4538}

    gal_bad_pix = {
        'iauname': 'J2',
        'fits_loc': '{}/example_bad_pix.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': '{}/example_bad_pix.png'.format(TEST_EXAMPLES_DIR),
        'ra': 146.714208787,
        'dec': -1.04128156958,
        'petroth50': 3.46419,
        'petroth90': 10.4538}

    gal_a = {
        'iauname': 'J3',
        'fits_loc': '{}/example_a.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': '{}/example_a.png'.format(TEST_EXAMPLES_DIR),
        'ra': 146.714208787,
        'dec': -1.04128156958,
        'petroth50': 3.46419,
        'petroth90': 10.4538}

    gal_b = {
        'iauname': 'J4',
        'fits_loc': '{}/example_b.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': '{}/example_b.png'.format(TEST_EXAMPLES_DIR),
        'ra': 146.631735209,
        'dec': -0.988354858412,
        'petroth50': 2.28976,
        'petroth90': 5.20297}

    gal_c = {
        'iauname': 'J5',
        'fits_loc': '{}/example_c.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': '{}/example_c.png'.format(TEST_EXAMPLES_DIR),
        # 'ra': 147.176446949,
        # 'dec': -0.354030416643,
        'ra': 146.631735209,
        'dec': -0.988354858412,
        'petroth50': 7.16148,
        'petroth90': 24.7535}

    gal_mystery = {
        'iauname': 'J121457.39-002412.7',
        'fits_loc': '/data/temp/J121457.39-002412.7.fits',
        'png_loc': '/data/temp/J121457.39-002412.7.png',
        'ra': 183.73974251,
        'dec': -0.403807422075,
        'petroth50': 7.16148,
        'petroth90': 24.7535}

    return Table([gal_missing, gal_incomplete, gal_bad_pix, gal_a, gal_b, gal_c, gal_mystery])


def test(fake_joint_catalog):
    """
    Create the NSA-DECaLS-GZ catalog, download fits, produce png, and identify new subjects

    Returns:
        None
    """

    data_release = '5'
    fits_dir = '/home/mike/temp'
    png_dir = '/home/mike/temp'
    # TEST_EXAMPLES_DIR = '/home/mike/temp'
    overwrite_fits = False
    overwrite_png = False

    # joint_catalog_loc = '/data/galaxy_zoo/decals/catalogs/nsa_v1_0_0_decals_dr5_first_1k.fits'
    # joint_catalog_loc = '/data/galaxy_zoo/decals/catalogs/nsa_v1_0_0_decals_dr5_last_1k.fits'
    # joint_catalog = Table(fits.getdata(joint_catalog_loc))
    joint_catalog = fake_joint_catalog
    joint_catalog['fits_loc'] = [get_fits_loc(fits_dir, galaxy) for galaxy in joint_catalog]
    joint_catalog['png_loc'] = [get_fits_loc(png_dir, galaxy) for galaxy in joint_catalog]

    _ = download_images_multithreaded(
        joint_catalog,
        data_release,
        fits_dir,
        png_dir,
        overwrite_fits=overwrite_fits,
        overwrite_png=overwrite_png)
#
if __name__ == '__main__':
    test(fake_joint_catalog())
