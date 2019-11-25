import pytest
from astropy.table import Table

import os
import numpy as np
from astropy.io import fits
from PIL import Image

from a_download_decals.get_images import download_images_threaded
from a_download_decals.get_images import image_utils

TEST_EXAMPLES_DIR = 'python/test_examples'


@pytest.fixture
def fits_dir(tmpdir):
    return tmpdir.mkdir('fits_dir').strpath


@pytest.fixture
def png_dir(tmpdir):
    return tmpdir.mkdir('png_dir').strpath


@pytest.fixture
def fits_loc(fits_dir):
    return fits_dir + '/' + 'test_image.fits'


@pytest.fixture
def png_loc(png_dir):
    return png_dir + '/' + 'test_image.png'


@pytest.fixture
def fits_image_params(fits_loc):
    return {
        'fits_loc': fits_loc,
        'ra': 114.5970,
        'dec': 21.5681,
        'zoomed_pixscale': 0.262,
        'max_size': 424,
        'data_release': '5'}


@pytest.fixture()
def small_galaxy(fits_loc, png_loc):
    return {
        'iauname': 'new_galaxy',
        'fits_loc': fits_loc,
        'png_loc': png_loc,
        'ra': 146.714208787,
        'dec': -1.04128156958,
        'petroth50': 3.46419,
        'petroth90': 10.4538
    }


@pytest.fixture
def extended_galaxy():
    # should have pixscale of about 1
    return {
        'ra': 216.0314,
        'dec': 34.8592,
        'iauname': 'extended',
        'petroth50': 1. / 0.04,
        'petroth90': 1. / 0.02
    }


@pytest.fixture
def fits_max_dimension():
    return 512


@pytest.fixture
def png_dimension():
    return 424


@pytest.fixture
def joint_catalog(fits_dir, png_dir):
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
        'ra': 146.631735209,
        'dec': -0.988354858412,
        'petroth50': 7.16148,
        'petroth90': 24.7535}

    return Table([gal_missing, gal_incomplete, gal_bad_pix, gal_a, gal_b, gal_c])


@pytest.fixture()
def partially_downloaded_galaxy_params(tmpdir):
    # copy the incomplete fits to a temporary directory
    dir = tmpdir.mkdir('incomplete_fits_dir').strpath
    temp_incomplete_example_loc = '{}/temp_incomplete_example.fits'.format(dir)
    incomplete_example_loc = '../test_examples/example_incomplete.fits'
    os.system('cp {} {}'.format(incomplete_example_loc, temp_incomplete_example_loc))
    # arguments required by download_fits_cutout
    return {
        'fits_loc': temp_incomplete_example_loc,
        'ra': 114.5970,
        'dec': 21.5681,
        'zoomed_pixscale': 0.262,
        'max_size': 424,
        'data_release': '5'}


def test_download_fits_cutout_retrieves_fits(fits_image_params):
    download_images_threaded.download_fits_cutout(**fits_image_params)
    hdulist = fits.open(fits_image_params['fits_loc'])
    matrix = hdulist[0].data

    channels = 3
    historical_size = 424
    arcsecs = historical_size * fits_image_params['zoomed_pixscale']
    native_pixscale = 0.262
    pixel_extent = np.ceil(arcsecs / native_pixscale).astype(int)
    assert matrix.shape == (channels, pixel_extent, pixel_extent)
    assert np.max(matrix) > 0
    assert np.min(matrix) <= 0


def test_download_fits_cutout_corrects_incomplete_fits(partially_downloaded_galaxy_params):
    assert not download_images_threaded.fits_downloaded_correctly(partially_downloaded_galaxy_params['fits_loc'])
    download_images_threaded.download_fits_cutout(**partially_downloaded_galaxy_params)
    assert download_images_threaded.fits_downloaded_correctly(partially_downloaded_galaxy_params['fits_loc'])


def test_get_download_quality_of_fits_on_missing_fits():
    downloaded, good_pix = download_images_threaded.get_download_quality_of_fits('nothing here')
    assert not downloaded
    assert not good_pix


def test_get_download_quality_of_fits_on_incomplete_fits():
    incomplete_fits_loc = '{}/example_incomplete.fits'.format(TEST_EXAMPLES_DIR)
    assert os.path.exists(incomplete_fits_loc)  # file exists
    downloaded, good_pix = download_images_threaded.get_download_quality_of_fits(incomplete_fits_loc)
    assert not downloaded  # file exists but is not completely downloaded
    assert not good_pix


def test_get_download_quality_of_fits_on_bad_pix_fits():
    partial_fits_loc = '{}/example_bad_pix.fits'.format(TEST_EXAMPLES_DIR)
    assert os.path.exists(partial_fits_loc)
    downloaded, good_pix = download_images_threaded.get_download_quality_of_fits(partial_fits_loc)
    assert downloaded
    assert not good_pix


def test_make_png_from_fits_creates_png(png_loc):
    fits_loc = '{}/example_a.fits'.format(TEST_EXAMPLES_DIR)
    assert os.path.exists(fits_loc)
    download_images_threaded.make_png_from_fits(fits_loc, png_loc, png_size=424)
    assert os.path.exists(png_loc)


def test_download_images_creates_fits_and_png(small_galaxy, fits_dir, png_dir):
    data_release = '5'
    assert not os.path.exists(small_galaxy['fits_loc'])
    assert not os.path.exists(small_galaxy['png_loc'])
    download_images_threaded.download_images(
        small_galaxy,
        data_release=data_release,
        overwrite_fits=False,
        overwrite_png=False)
    assert download_images_threaded.fits_downloaded_correctly(small_galaxy['fits_loc'])
    assert os.path.exists(small_galaxy['png_loc'])


def test_check_images_are_downloaded(joint_catalog):
    # directly on test_examples directory
    checked_catalog = download_images_threaded.check_images_are_downloaded(joint_catalog)
    print(checked_catalog[['iauname', 'fits_ready', 'fits_filled', 'png_ready']])
    assert np.array_equal(checked_catalog['fits_ready'], np.array([False, False, True, True, True, True]))
    assert np.array_equal(checked_catalog['fits_filled'], np.array([False, False, False, True, True, True]))
    assert np.array_equal(checked_catalog['png_ready'], np.array([False, False, True, True, True, True]))


def test_download_images_multithreaded(joint_catalog, fits_dir, png_dir):
    data_release = '5'

    # download to new temporary directory
    joint_catalog['fits_loc'] = [download_images_threaded.get_loc(fits_dir, galaxy, 'fits') for galaxy in joint_catalog]
    joint_catalog['png_loc'] = [download_images_threaded.get_loc(png_dir, galaxy, 'png') for galaxy in joint_catalog]

    # verify files are not already downloaded
    for galaxy in joint_catalog:
        assert not os.path.exists(galaxy['fits_loc'])
        assert not os.path.exists(galaxy['png_loc'])

    # run download
    output_catalog = download_images_threaded.download_images_multithreaded(
        joint_catalog,
        data_release,
        fits_dir,
        png_dir,
        overwrite_fits=False,
        overwrite_png=False)

    # verify files are now downloaded (to some unknown quality)
    for galaxy in output_catalog:
        assert os.path.exists(galaxy['fits_loc'])
        assert os.path.exists(galaxy['png_loc'])

    # verify catalog correctly reports as now downloaded
    np.array_equal(output_catalog['fits_ready'], np.ones(len(output_catalog), dtype=bool))
    np.array_equal(output_catalog['fits_filled'], np.ones(len(output_catalog), dtype=bool))
    np.array_equal(output_catalog['png_ready'], np.ones(len(output_catalog), dtype=bool))


def test_download_images_creates_fits_and_png_small(small_galaxy, fits_dir, png_dir, fits_max_dimension, png_dimension):
    data_release = '5'
    small_galaxy['fits_loc'] = '{}/extended.fits'.format(fits_dir)
    small_galaxy['png_loc'] = '{}/extended.png'.format(png_dir)
    assert not os.path.exists(small_galaxy['fits_loc'])
    assert not os.path.exists(small_galaxy['png_loc'])
    download_images_threaded.download_images(
        small_galaxy,
        data_release=data_release,
        overwrite_fits=False,
        overwrite_png=False)
    # check download succeeded
    assert download_images_threaded.fits_downloaded_correctly(small_galaxy['fits_loc'])
    assert os.path.exists(small_galaxy['png_loc'])
    # check fits is smaller than 424x424
    fits_img = fits.getdata(small_galaxy['fits_loc'])
    assert fits_img.size < fits_max_dimension * fits_max_dimension * 3
    # check small fits accurately resized to 424x424
    assert np.array(Image.open(small_galaxy['png_loc'])).shape == (png_dimension, png_dimension, 3)


def test_download_images_creates_fits_and_png_extended(extended_galaxy, fits_dir, png_dir, fits_max_dimension, png_dimension):
    data_release = '5'
    extended_galaxy['fits_loc'] = '{}/extended.fits'.format(fits_dir)
    extended_galaxy['png_loc'] = '{}/extended.png'.format(png_dir)
    assert not os.path.exists(extended_galaxy['fits_loc'])
    assert not os.path.exists(extended_galaxy['png_loc'])
    download_images_threaded.download_images(
        extended_galaxy,
        data_release=data_release,
        overwrite_fits=False,
        overwrite_png=False)
    # check download succeeded
    assert download_images_threaded.fits_downloaded_correctly(extended_galaxy['fits_loc'])
    assert os.path.exists(extended_galaxy['png_loc'])
    # check fits is exactly 424x424 (max size)
    fits_img = fits.getdata(extended_galaxy['fits_loc'])
    assert fits_img.size == fits_max_dimension * fits_max_dimension * 3
    # check png is also 424x424
    assert np.array(Image.open(extended_galaxy['png_loc'])).shape == (png_dimension, png_dimension, 3)


def test_save_example_png(png_dimension):
    img_data = fits.getdata('{}/example_e.fits'.format(TEST_EXAMPLES_DIR))
    img = image_utils.get_dr2_style_image(img_data)
    download_images_threaded.save_carefully_resized_png(
        '{}/example_flipped_png.png'.format(TEST_EXAMPLES_DIR),
        img,
        png_dimension)
