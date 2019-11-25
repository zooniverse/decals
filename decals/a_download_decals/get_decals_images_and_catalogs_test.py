import os

import numpy as np
import pytest
from PIL import Image

from a_download_decals.get_decals_images_and_catalogs import *


@pytest.fixture()
def fits_dir(tmpdir):
    return tmpdir.mkdir('fits_dir').strpath


@pytest.fixture()
def png_dir(tmpdir):
    return tmpdir.mkdir('png_dir').strpath


@pytest.fixture()
def catalog_dir(tmpdir):
    return tmpdir.mkdir('catalog_dir').strpath


@pytest.fixture()
def joint_catalog_loc(catalog_dir):
    return '{}/joint_catalog.fits'.format(catalog_dir)


@pytest.fixture()
def nsa():
    return Table([
        {
            'iauname': 'iau_small',
            'nsa_id': '0',
            'ra': 10.,
            'dec': -1.,
            'petrotheta': 1.,
            'petroth50': 3.5,
            'petroth90': 10.,
            'z': 0.01,
            'nsa_version': '1_0_0'
        },

        {
            'iauname': 'iau_far',
            'nsa_id': '1',
            'ra': 10.,
            'dec': -1.,
            'petrotheta': 4.,
            'petroth50': 3.5,
            'petroth90': 10.,
            'z': 1.,
            'nsa_version': '1_0_0'
        },

        {
            'iauname': 'iau_below_bricks',
            'nsa_id': '2',
            'ra': 10.,
            'dec': -100.,
            'petrotheta': 4.,
            'petroth50': 3.5,
            'petroth90': 10.,
            'z': .01,
            'nsa_version': '1_0_0'
        },

        {
            'iauname': 'iau_outside_bricks',
            'nsa_id': '3',
            'ra': 100.,
            'dec': -1.,
            'petrotheta': 4.,
            'petroth50': 3.5,
            'petroth90': 10.,
            'z': .01,
            'nsa_version': '1_0_0'
        },

        {
            'iauname': 'iau_good_subject',
            'nsa_id': '5',
            'ra': 10.,
            'dec': -1.,
            'petrotheta': 4.,
            'petroth50': 3.5,
            'petroth90': 10.,
            'z': .01,
            'nsa_version': '1_0_0'
        },

    ])


@pytest.fixture()
def bricks():
    return Table([
        # galaxies RA 0->90 and dec -10->10 should match
        {
            'ra1': 0.,
            'ra': 45.,
            'ra2': 90.,
            'dec1': -10.,
            'dec': 0.,
            'dec2': 10.
        },

        # galaxies RA 90->110 should fail to match
        # galaxies RA 110->270 and dec - 10->10 should match
        {
            'ra1': 110.,
            'ra': 185.,
            'ra2': 360.,
            'dec1': -10.,
            'dec': 0.,
            'dec2': 10.
        },

        # galaxies RA = 270->360 should multiple-match
        {
            'ra1': 270.,
            'ra': 315.,
            'ra2': 360.,
            'dec1': -10.,
            'dec': 0.,
            'dec2': 10.
        },
    ])


@pytest.fixture()
def previous_subjects():
    return pd.DataFrame([
        # DR1 entries have provided_image_id filled with iau name, nsa_id blank, dr blank
        {'_id': 'ObjectId(0)',
         'zooniverse_id': 'gz_a',
         'provided_image_id': 'iau_previous_dr1_subject',
         'nsa_id': np.nan,
         'dr': np.nan
         },

        # DR2 entries have provided_image_id blank, nsa_id filled with NSA_[number], dr filled with 'DR2'
        {'_id': 'ObjectId(1)',
         'zooniverse_id': 'gz_b',
         'provided_image_id': np.nan,
         'nsa_id': 'NSA_5',  # nsa id matches 'iau_previous_dr2_subject'
         'dr': 'DR2'
         }
    ])


class SettingsMockObject():
    # settings is imported as a file ('import settings.py'). Mirror that behaviour (e.g. dot access) with a class.
    def __init__(self, catalog_dir, fits_dir, png_dir, data_release, nsa_version, joint_catalog_loc):
        self.catalog_dir = catalog_dir
        self.fits_dir = fits_dir
        self.png_dir = png_dir
        self.data_release = data_release
        self.nsa_version = nsa_version
        self.joint_catalog_loc = joint_catalog_loc


@pytest.fixture()
def settings(catalog_dir, fits_dir, png_dir, joint_catalog_loc):
    return SettingsMockObject(
        catalog_dir=catalog_dir,
        fits_dir=fits_dir,
        png_dir=png_dir,
        data_release='3',
        nsa_version='1_0_0',
        joint_catalog_loc=joint_catalog_loc)


def test_get_decals(nsa, bricks, settings):
    # these settings are specified separately
    settings.new_catalog = True
    settings.new_images = True
    settings.overwrite_fits = True
    settings.overwrite_png = True
    settings.run_to = None

    catalog = get_decals(nsa, bricks, settings)

    assert os.path.exists(settings.joint_catalog_loc)
    # saved_catalog = Table.read(settings.joint_catalog_loc)
    # assert catalog == saved_catalog

    remaining_names = set(catalog['iauname'])
    assert 'iau_small' not in remaining_names
    assert 'iau_below_bricks' not in remaining_names
    assert 'iau_outside_bricks' not in remaining_names
    assert 'iau_good_subject' in remaining_names
    assert 'iau_far' in remaining_names  # no redshift filtering

    new_subject = catalog[0]

    # fits downloaded, has values
    assert os.path.exists(new_subject['fits_loc'])
    img = fits.getdata(new_subject['fits_loc'])
    assert np.max(img) > 0
    assert np.min(img) <= 0
    assert new_subject['fits_ready']
    assert new_subject['fits_filled']

    # png downloaded, has values
    assert os.path.exists(new_subject['png_loc'])
    png = Image.open(new_subject['png_loc'])
    png_matrix = np.array(png)
    assert np.max(png_matrix) > 0
    assert np.min(png_matrix) <= 0
    assert new_subject['png_ready']
