import pytest
from astropy.table import Table

from b_to_zooniverse.do_upload import manifest

TEST_EXAMPLES_DIR = 'python/test_examples'


@pytest.fixture()
def joint_catalog():
    return Table([
        {
            'nsa_id': 'example_nsa_id',
            'iauname': 'example_iauname',
            'ra': 147.45674,
            'dec': 1.09255,
            'petroth50': 50.,
            'petrotheta': 4.,
            'petroflux': [20., 21., 22., 23., 24., 25., 26.],
            'nsa_version': '1_0_0',
            'z': 0.1,
            'mag': [0., 1., 2., 3., 4., 5., 6.],
            'absmag': [10., 11., 12., 13., 14., 15., 16.],
            'nmgy': [30., 31., 32., 33., 34., 35., 36.],
            'png_loc': 'jpeg_here.png',
            'fits_loc': 'fits_there.fits'
        }
    ])


@pytest.fixture()
def joint_catalog_masked():
    masked_table = Table([
        {
            'nsa_id': 'example_nsa_id',
            'iauname': 'example_iauname',
            'ra': 147.45674,
            'dec': 1.09255,
            'petroth50': 50.,
            'petrotheta': 4.,
            'petroflux': [20., 21., 22., 23., 24., 25., 26.],
            'nsa_version': '1_0_0',
            'z': 0.1,
            'mag': [0., 1., 2., 3., 4., 5., 6.],
            'absmag': [10., 11., 12., 13., 14., 15., 16.],
            'nmgy': [30., 31., 32., 33., 34., 35., 36.],
            'png_loc': 'jpeg_here.png',
            'fits_loc': 'fits_there.fits'
        }
    ],
    masked=True)

    masked_table['nmgy'].mask = [[True, False, False, False, False, False, False]]  # mask entry for mag_faruv
    return masked_table


@pytest.fixture()
def calibration_catalog():
    return Table([
        {
            'nsa_id': 'example_nsa_id',
            'iauname': 'example_iauname',
            'ra': 147.45674,
            'dec': 1.09255,
            'petroth50': 50.,
            'petrotheta': 4.,
            'petroflux': [20., 21., 22., 23., 24., 25., 26.],
            'nsa_version': '1_0_0',
            'z': 0.1,
            'mag': [0., 1., 2., 3., 4., 5., 6.],
            'absmag': [10., 11., 12., 13., 14., 15., 16.],
            'nmgy': [30., 31., 32., 33., 34., 35., 36.],
            'png_loc': 'do_not_use.png',
            'fits_loc': 'fits_there.fits',
            'dr2_png_loc': 'type_dr2.png',
            'colour_png_loc': 'type_colour.png'
        }
    ])


def test_create_manifest_from_joint_catalog(joint_catalog):
    new_manifest = manifest.create_manifest_from_joint_catalog(joint_catalog)
    assert len(new_manifest) == len(joint_catalog)
    entry = new_manifest[0]
    assert entry['png_loc'] == 'jpeg_here.png'
    assert type(entry['key_data']) == dict
    assert entry['key_data']['!ra'] == 147.45674
    assert type(entry['key_data']['!sdss_search'] == str)
    assert type(entry['key_data']['!decals_search'] == str)
    assert type(entry['key_data']['!simbad_search'] == str)
    assert type(entry['key_data']['!nasa_ned_search'] == str)


def test_create_manifest_from_joint_catalog_with_masks(joint_catalog_masked):
    new_manifest = manifest.create_manifest_from_joint_catalog(joint_catalog_masked)
    assert len(new_manifest) == len(joint_catalog_masked)
    entry = new_manifest[0]
    assert entry['png_loc'] == 'jpeg_here.png'
    assert type(entry['key_data']) == dict
    assert entry['key_data']['!ra'] == 147.45674
    assert entry['key_data']['!mag_faruv'] == -999.
    assert type(entry['key_data']['!sdss_search'] == str)
    assert type(entry['key_data']['!decals_search'] == str)
    assert type(entry['key_data']['!simbad_search'] == str)
    assert type(entry['key_data']['!nasa_ned_search'] == str)


def test_create_manifest_from_calibration_catalog(calibration_catalog):
    image_columns = ['dr2_png_loc', 'colour_png_loc']
    new_manifest = manifest.create_manifest_from_calibration_catalog(calibration_catalog, image_columns)
    assert len(new_manifest) == len(calibration_catalog) * 2

    first_entry = new_manifest[0]
    assert first_entry['png_loc'] == 'type_dr2.png'
    assert type(first_entry['key_data']) == dict
    assert first_entry['key_data']['!ra'] == 147.45674

    last_entry = new_manifest[-1]
    assert last_entry['png_loc'] == 'type_colour.png'
    assert type(last_entry['key_data']) == dict
    assert last_entry['key_data']['!ra'] == 147.45674


def test_coords_to_decals_skyviewer(joint_catalog):
    galaxy = joint_catalog[0]
    url = manifest.coords_to_decals_skyviewer(galaxy['ra'], galaxy['dec'])
    print(url)
    # TODO I don't know how to programmatically test that this query works, beyond not falling over


def test_coords_to_sdss_navigate(joint_catalog):
    galaxy = joint_catalog[0]
    url = manifest.coords_to_sdss_navigate(galaxy['ra'], galaxy['dec'])
    print(url)
    # TODO I don't know how to programmatically test that this query works, beyond not falling over


def test_coords_to_simbad(joint_catalog):
    galaxy = joint_catalog[0]
    url = manifest.coords_to_simbad(galaxy['ra'], galaxy['dec'], search_radius=10.)
    print(url)
    # TODO I don't know how to programmatically test that this query works, beyond not falling over


def test_coords_to_ned(joint_catalog):
    galaxy = joint_catalog[0]
    url = manifest.coords_to_ned(galaxy['ra'], galaxy['dec'], search_radius=10.)
    print(url)
    # TODO I don't know how to programmatically test that this query works, beyond not falling over


def test_coords_to_vizier(joint_catalog):
    galaxy = joint_catalog[0]
    url = manifest.coords_to_vizier(galaxy['ra'], galaxy['dec'], search_radius=10.)
    print(url)
    # TODO I don't know how to programmatically test that this query works, beyond not falling over


def test_replace_bytes_with_str():

    byt = b'J094552.53-000534.1'
    assert type(byt) == bytes
    assert type(byt) != str
    string = manifest.replace_bytes_with_str(byt)
    assert type(string) == str
    print(string)

    not_byt = 'hello world'
    string = manifest.replace_bytes_with_str(not_byt)
    assert type(string) == str
