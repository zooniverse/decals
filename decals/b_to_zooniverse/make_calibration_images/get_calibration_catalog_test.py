import pytest

from astropy.table import Table

from b_to_zooniverse.make_calibration_images import get_calibration_catalog


@pytest.fixture()
def expert_catalog():
    # expert catalog uses iau name at 2dp (originally 'sdss')
    return Table([
        {'SDSS': 'gz_a_2dp',
         '_RA': 10.,
         '_DE': 10.,
         'BAR': 2 ** 5,
         'RING': 2 ** 3},

        {'SDSS': 'gz_b_2dp',
         '_RA': 20.,
         '_DE': 20.,
         'BAR': 2 ** 3,
         'RING': 2 ** 1}
    ])


@pytest.fixture()
def joint_catalog():
    # joint catalog uses iau name at 1dp
    return Table([
        {'iauname': 'gz_a_1dp',
         'ra': 10.,
         'dec': 10.,
         'feature': 'value_1'},

        {'iauname': 'gz_b_1dp',
         'ra': 90.,
         'dec': 90.,
         'feature': 'value_2'}
    ])


def test_decode_binary_mask():
    decoded_ints = get_calibration_catalog.decode_binary_mask(2 ** 2 + 2 ** 3)
    assert decoded_ints == [2, 3]

    decoded_ints = get_calibration_catalog.decode_binary_mask(2 ** 4)
    assert decoded_ints == [4]

    decoded_ints = get_calibration_catalog.decode_binary_mask(0)
    assert decoded_ints == []


def test_decode_bar_ints():

    peanut_bar = get_calibration_catalog.decode_bar_ints(2 ** 5)
    assert peanut_bar == ['peanut']

    weak_and_nuclear = get_calibration_catalog.decode_bar_ints(2 ** 3 + 2 ** 6)
    assert weak_and_nuclear == ['weak', 'nuclear']


def test_decode_ring_ints():

    inner_ring = get_calibration_catalog.decode_ring_ints(2 ** 2)
    assert inner_ring == ['inner']

    nuclear_and_outer = get_calibration_catalog.decode_ring_ints(2 ** 1 + 2 ** 3)
    assert nuclear_and_outer == ['nuclear', 'outer']


def test_interpret_expert_catalog(expert_catalog):

    expected_catalog = Table([{
        'iauname': 'gz_a_2dp',
        'ra': 10.,
        'dec': 10.,
        'bar': 2 ** 5,
        'ring': 2 ** 3,
        'has_bar': True,
        'has_ring': True,
        'bar_types': ['peanut'],
        'ring_types': ['outer'],
    }])

    interpreted_catalog = get_calibration_catalog.interpret_expert_catalog(expert_catalog)

    # not clear why this requires considering both cases, but test below passes fine TODO
    for col in set(expected_catalog.colnames):
        interpreted_value = interpreted_catalog[0][col]
        expected_value = expected_catalog[0][col]
        # more descriptive than assert Table equal
        if type(interpreted_catalog[0][col]) == list:
            assert set(expected_value) == set(interpreted_value)
        else:
            assert expected_value == interpreted_value


def test_get_expert_catalog_joined_with_decals(joint_catalog, expert_catalog):

    interpreted_catalog = get_calibration_catalog.interpret_expert_catalog(expert_catalog)  # not independent

    joined_catalog = get_calibration_catalog.get_expert_catalog_joined_with_decals(joint_catalog, interpreted_catalog)
    assert len(joined_catalog) == 1

    expected_catalog = Table([{
        'iauname': 'gz_a_1dp',
        'iauname_expert': 'gz_a_2dp',
        'feature': 'value_1',
        'ra': 10.,
        'ra_expert': 10.,
        'dec': 10.,
        'dec_expert': 10.,
        'bar': 2 ** 5,
        'ring': 2 ** 3,
        'has_bar': True,
        'has_ring': True,
        'bar_types': ['peanut'],
        'ring_types': ['outer'],
        'best_match': 0,
        'sky_separation': 0.0
    }])

    for col in set(expected_catalog.colnames + joined_catalog.colnames):
        # print(col)
        # print(joined_catalog[0][col])
        # print(expected_catalog[0][col])
        assert all(joined_catalog[col] == expected_catalog[col])  # more descriptive than assert Table equal
