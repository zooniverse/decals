import numpy as np
from astropy.table import Table
from astropy.io import fits
from astropy import units as u
import pandas as pd

import matplotlib.pyplot as plt

from shared_astro_utils import matching_utils


def get_expert_catalog_joined_with_decals(decals_catalog, expert_catalog, plot=False):
    """
    Match Nair 2010 to the joint nsa-decals catalog. Decode Nair's binary type encoding.
    Add convenience columns to indicate bar or ring. Optionally, plot bar/ring statistics.
    Args:
        decals_catalog (astropy.Table): catalog of nsa galaxies in decals
        expert_catalog (astropy.Table): Nair 2010 expert classifications
        plot (bool): if True, make bar charts of T-Type, Bar and Ring counts in output catalog

    Returns:
        (astropy.Table): matched catalog, with extra bar/ring columns
    """
    output_catalog, _ = matching_utils.match_galaxies_to_catalog_table(
        galaxies=expert_catalog,
        catalog=decals_catalog,
        matching_radius=5 * u.arcsec,
        galaxy_suffix='_expert')

    if plot:
        save_output_catalog_statistics(output_catalog)

    return output_catalog


def get_expert_catalog(expert_catalog_loc, save_loc=None):
    catalog = Table(fits.getdata(expert_catalog_loc))
    catalog = interpret_expert_catalog(catalog)
    if save_loc is not None:
        catalog.to_pandas().to_csv(save_loc, encoding='utf-8', index=False)
    return catalog


def interpret_expert_catalog(catalog):
    # convert column names to be consistent with nsa
    for column_name in catalog.colnames:
        catalog.rename_column(column_name, column_name.lower())
    catalog.rename_column('sdss', 'iauname')
    catalog.rename_column('_ra', 'ra')
    catalog.rename_column('_de', 'dec')

    catalog['has_bar'] = catalog['bar'] != 0
    catalog['has_ring'] = catalog['ring'] != 0

    catalog['bar_types'] = list(map(decode_bar_ints, catalog['bar']))
    catalog['ring_types'] = list(map(decode_ring_ints, catalog['ring']))

    return catalog


def decode_bar_ints(encoded_int):
    bar_int_labels = decode_binary_mask(encoded_int)
    return [bar_int_label_to_str(label) for label in bar_int_labels]


def decode_ring_ints(encoded_int):
    ring_int_labels = decode_binary_mask(encoded_int)
    return [ring_int_label_to_str(label) for label in ring_int_labels]


def decode_binary_mask(encoded_int):
    """
    Nair 2010 encodes classifications as sum over n ((2^n), where n is each classification type
    Undo the encoding to find each n
    For example, convert 8 -> 2^3 -> [3]
    Args:
        encoded_int (int): value = sum(2^n)

    Returns:
        (list): decoded ints e.g. 6 -> [1, 2]
    """
    # convert to binary base, represent as string
    binary_int_string = bin(encoded_int)[2:]
    # convert to array
    binary_int_array = np.array([int(x) for x in binary_int_string])
    # reading right to left, count off the index of each 1
    # flip and then get left-to-right index of nonzero elements
    indices_of_nonzero = np.nonzero(np.flip(binary_int_array, axis=0))[0]
    return list(indices_of_nonzero)


def bar_int_label_to_str(bar_int_label):
    mapping = {
        1: 'strong',
        2: 'intermediate',
        3: 'weak',
        4: 'ansae',
        5: 'peanut',
        6: 'nuclear',
        7: 'unsure'
    }
    return mapping[bar_int_label]


def ring_int_label_to_str(ring_int_label):
    """
    Binary encoding only works when you can only have at most one of each type
    e.g. one inner 2^2 = 4 = 2^1 + 2^1 = two nuclear
    There are many examples of e.g. '36' which could be four outer rings, three outer and two inner, etc.
    This seems a silly way to encode data - maybe I have misunderstood?
    Especially, some seem insanely high - having at least 8 rings is implausible
    See e.g. row 48: ring type 76 i.e. 64 (8 * outer ring) + 8 (outer ring) + 4 (inner ring)...?
    http://skyserver.sdss.org/dr12/SkyserverWS/ImgCutout/getjpeg?ra=211.21558&dec=-00.641614&width=512&height=512

    Args:
        ring_int_label (int): decoded int e.g. 2

    Returns:
        (str) human-readable label, paraphrased from Nair 2010 definitions
    """
    mapping = {
        1: 'nuclear',
        2: 'inner',  # or two nuclear...
        3: 'outer',  # or two inner...
        4: 'min_two',
        5: 'min_four',
        6: 'min_eight'
    }
    return mapping[ring_int_label]


def save_output_catalog_statistics(output_catalog):
    output_catalog = output_catalog[['tt', 'has_bar', 'has_ring']].to_pandas()

    output_catalog['tt'].value_counts().sort_index().plot(kind='bar')
    plt.ylabel('Count')
    plt.xlabel('T-Type of Nair galaxy in DECALS DR5')
    plt.tight_layout()
    plt.savefig('ttype_counts.png')
    plt.clf()

    output_catalog['has_bar'].value_counts().sort_index().plot(kind='bar')
    plt.ylabel('Count')
    plt.xlabel('Bar of Nair galaxy in DECALS DR5')
    plt.tight_layout()
    plt.savefig('bar_counts.png')
    plt.clf()

    output_catalog['has_ring'].value_counts().sort_index().plot(kind='bar')
    plt.ylabel('Count')
    plt.xlabel('Ring of Nair galaxy in DECALS DR5')
    plt.tight_layout()
    plt.savefig('ring_counts.png')
    plt.clf()


def column_value_counts_as_dataframe(data, column):
    counts = pd.Series(data[column]).value_counts()
    return pd.DataFrame({column: counts.index, 'count': counts.values})
