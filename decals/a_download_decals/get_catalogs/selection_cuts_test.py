
import pytest

from a_download_decals.get_catalogs.selection_cuts import apply_selection_cuts
from astropy.table import Table


@pytest.fixture()
def catalog():

    # DR5 is from 0-360 in RA and -20 to +30 in Dec
    return Table([
        {'iauname': 'gal_a',
         'ra': 150.,
         'dec': 3.,  # in Dec window
         'z': 0.01,
         'petrotheta': 5.},  # above minimum petrotheta

        # adversarial example identical to gal_a
        {'iauname': 'gal_a_duplicate',
         'ra': 150.,
         'dec': 3.,  # in Dec window
         'z': 0.01,
         'petrotheta': 5.},  # above minimum petrotheta

        {'iauname': 'gal_a_small',
         'ra': 150.,
         'dec': 3.,  # in Dec window
         'z': 0.01,
         'petrotheta': 1.},  # below minimum petrotheta

        {'iauname': 'gal_a_negative_size',
         'ra': 150.,
         'dec': 3.,  # in Dec window
         'z': 0.01,
         'petrotheta': -1.},  # below minimum petrotheta, adversarial example

        {'iauname': 'gal_a_far',
         'ra': 150.,
         'dec': 3.,  # in Dec window
         'z': 1.,
         'petrotheta': 5.},  # above minimum petrotheta
    ])


def test_apply_selection_cuts(catalog):
    filtered_catalog = apply_selection_cuts(catalog)
    remaining_names = set(filtered_catalog['iauname'])

    assert 'gal_a' in remaining_names  # normal galaxy
    assert 'gal_a_duplicate' in remaining_names

    assert 'gal_a_small' not in remaining_names
    assert 'gal_a_negative_size' not in remaining_names
    assert 'gal_a_far' in remaining_names  # there should be no redshift filtering, only petrotheta
