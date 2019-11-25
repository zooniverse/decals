import pytest

from astropy.table import Table

from a_download_decals.setup.join_brick_tables import *


@pytest.fixture()
def coordinate_catalog():
    return Table([
        {'ra': 1.0,
         'dec': 11.0,
         'example_edge': 0.5,
         'brickname': 'simple_match'},

        {'ra': 2.0,
         'dec': 12.0,
         'example_edge': 1.5,
         'brickname': 'bad_name'},
    ])


@pytest.fixture()
def exposure_catalog():
    return Table([
        {'ra': 1.0,
         'dec': 11.0,
         'exposures': 1,
         'brickname': 'simple_match'
         },

        {'ra': 2.0,
         'dec': 12.0,
         'exposures': 0,
         'brickname': 'bad_name_different'},  # name is not the same - should not join
    ])


def test_merge_brick_tables(coordinate_catalog, exposure_catalog):
    brick_catalog = merge_bricks_catalogs(coordinate_catalog, exposure_catalog, test_mode=True)
    matched_bricks = set(brick_catalog['brickname'])

    assert 'simple_match' in matched_bricks
    assert 'bad_name' not in matched_bricks
