import pytest

import os
import shutil

from astropy.table import Table

from b_to_zooniverse.make_calibration_images import get_calibration_images
from a_download_decals.get_images.download_images_threaded import get_loc
from a_download_decals.get_images.image_utils import get_dr2_style_image


TEST_EXAMPLES_DIR = 'python/test_examples'


@pytest.fixture
def png_dir(tmpdir):
    return tmpdir.mkdir('png_dir').strpath


@pytest.fixture
def png_loc(png_dir):
    return png_dir + '/temp.png'


@pytest.fixture
def galaxy(png_loc):
    return {
        'iauname': 'J104356',
        'fits_loc': '{}/example_a.fits'.format(TEST_EXAMPLES_DIR),
        'png_loc': png_loc
    }


@pytest.fixture
def catalog():
    return Table([
        {
            'iauname': 'J104356',
            'fits_loc': '{}/example_a.fits'.format(TEST_EXAMPLES_DIR),
        },

        {
            'iauname': 'J104357',
            'fits_loc': '{}/example_b.fits'.format(TEST_EXAMPLES_DIR),
        }
    ])


def test_save_image_of_galaxy(galaxy, png_loc):
    assert not os.path.exists(png_loc)
    get_calibration_images.save_image_of_galaxy(galaxy, size=424, img_creator_func=get_dr2_style_image)
    assert os.path.exists(png_loc)


def test_save_png_image_of_galaxy(catalog, png_dir):
    expected_png_locs = [get_loc(png_dir, galaxy, 'png') for galaxy in catalog]
    assert not any([os.path.exists(expected_png_loc) for expected_png_loc in expected_png_locs])
    get_calibration_images.make_catalog_png_images(catalog, get_dr2_style_image, png_dir, size=424, n_processes=1)
    assert all([os.path.exists(expected_png_loc) for expected_png_loc in expected_png_locs])


def test_save_png_image_of_galaxy_missing_dir(catalog, png_dir):
    missing_dir = '{}/{}'.format(png_dir, 'some_other_dir')
    os.mkdir(missing_dir)  # temporarily created in order to be able to safely  construct expected locations
    expected_png_locs = [get_loc(missing_dir, galaxy, 'png') for galaxy in catalog]
    assert not any([os.path.exists(expected_png_loc) for expected_png_loc in expected_png_locs])
    shutil.rmtree(missing_dir)  # remove again, including the empty folders that get_loc creates
    assert not os.path.isdir(missing_dir)

    get_calibration_images.make_catalog_png_images(catalog, get_dr2_style_image, missing_dir, size=424, n_processes=1)
    assert os.path.isdir(missing_dir)
    assert all([os.path.exists(expected_png_loc) for expected_png_loc in expected_png_locs])
