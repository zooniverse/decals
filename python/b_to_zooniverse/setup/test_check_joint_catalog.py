import pytest

from astropy.table import Table

from b_to_zooniverse.setup.check_joint_catalog import enforce_joint_catalog_columns
from b_to_zooniverse import to_zooniverse_settings as settings
from b_to_zooniverse.setup import check_joint_catalog


@pytest.fixture
def joint_catalog():
    # actual values for first two NSA v1_0_1 galaxies
    return Table([
        {
            'ra': 146.714215072841,
            'dec': -1.0412800233313741,
            'fits_loc': 'dir/some_fits.fits',
            'png_loc': 'dir/some_png.png'
        },

        {
            'ra': 146.6285851269414,
            'dec': -0.7651620976591762,
            'fits_loc': 'dir/some_fits.fits',
            'png_loc': 'dir/some_png.png'
        }
    ])


@pytest.fixture
def nsa_cached():
    # actual values for first two NSA v1_0_1 galaxies
    return Table([
        {
            'nsa_id': 1,
            'iauname': 'J094651.40-010228.5',
            'ra': 146.714215072841,
            'dec': -1.0412800233313741,
            'petroth50': 50.,
            'petrotheta': 4.,
            'petroflux': [20., 21., 22., 23., 24., 25., 26.],
            'nsa_version': '1_0_0',
            'z': 0.1,
            'mag': [0., 1., 2., 3., 4., 5., 6.],
            'absmag': [10., 11., 12., 13., 14., 15., 16.],
            'nmgy': [30., 31., 32., 33., 34., 35., 36.],
        },

        {
            'nsa_id': 2,
            'iauname': 'J094630.85-004554.5',
            'ra': 146.6285851269414,
            'dec': -0.7651620976591762,
            'petroth50': 50.,
            'petrotheta': 4.,
            'petroflux': [20., 21., 22., 23., 24., 25., 26.],
            'nsa_version': '1_0_0',
            'z': 0.1,
            'mag': [0., 1., 2., 3., 4., 5., 6.],
            'absmag': [10., 11., 12., 13., 14., 15., 16.],
            'nmgy': [30., 31., 32., 33., 34., 35., 36.],
        }]
    )


def test_enforce_joint_catalog_columns_with_cache(joint_catalog, nsa_cached, monkeypatch):

    # when calling check_joint_catalog, replace_get_nsa_catalog with dummy function
    # dummy function uses the fixtures instead of really loading the NSA catalog
    def mock_get_nsa_catalog(nsa_loc='', nsa_version=''):
        if nsa_loc == settings.nsa_cached_loc:
            return nsa_cached
        elif nsa_loc == settings.nsa_catalog_loc:
            nsa = nsa_cached.copy()
            nsa['some_other_column'] = ['a' for n in range(len(nsa))]
            return nsa
    monkeypatch.setattr(check_joint_catalog, 'get_nsa_catalog', mock_get_nsa_catalog)

    # when calling Table.read / Table.write in cache_table (under shared_astro_utilities/astropy_utils),
    # don't actually read or write!
    def mock_read_table(target_loc):  # don't actually load the cached nsa catalog
        assert target_loc == settings.nsa_cached_loc
        return nsa_cached
    monkeypatch.setattr('shared_astro_utilities.astropy_utils.Table.read', mock_read_table)

    def mock_write_table(self, target_loc, overwrite):  # don't actually save any files
        assert target_loc == settings.nsa_cached_loc
    monkeypatch.setattr('shared_astro_utilities.astropy_utils.Table.write', mock_write_table)

    new_joint_catalog = enforce_joint_catalog_columns(joint_catalog)
    assert len(new_joint_catalog) == len(joint_catalog)
    for nsa_col in nsa_cached.colnames:  # all cached columns are now in joint catalog
        assert nsa_col in set(new_joint_catalog.colnames)
