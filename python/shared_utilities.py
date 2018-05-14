import datetime
import json
import logging

import pandas as pd
import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.table import Table
from astropy import table
from astropy.io import fits

# don't know how to install conda modules on travis
# import datashader as ds
# import datashader.transfer_functions as tf
# from datashader.utils import export_image



# def plot_catalog(catalog, filename, column_to_colour=None):
#     """
#
#     Args:
#         catalog ():
#         filename ():
#         column_to_colour ():
#
#     Returns:
#
#     """
#     canvas = ds.Canvas(plot_width=300, plot_height=300)
#     if column_to_colour:  # shade pixels by average value in column_to_colour
#         aggc = canvas.points(catalog, 'ra', 'dec', ds.mean(column_to_colour))
#     else:
#         aggc = canvas.points(catalog, 'ra', 'dec')
#     img = tf.shade(aggc)
#     export_image(img, filename)
#
#
# def plot_catalog_overlap(catalog_a, catalog_b, legend, filename):
#     """
#
#     Args:
#         catalog_a ():
#         catalog_b ():
#         legend ():
#         filename ():
#
#     Returns:
#
#     """
#
#     a_coords = catalog_a[['ra', 'dec']]
#     a_coords['catalog'] = legend[0]
#     b_coords = catalog_b[['ra', 'dec']]
#     b_coords['catalog'] = legend[1]
#
#     df_to_plot = pd.concat([a_coords, b_coords])
#     df_to_plot['catalog'] = df_to_plot['catalog'].astype('category')
#
#     canvas = ds.Canvas(plot_width=300, plot_height=300)
#     aggc = canvas.points(df_to_plot, 'ra', 'dec', ds.count_cat('catalog'))
#     img = tf.shade(aggc)
#     export_image(img, filename)

# pandas version
# def match_galaxies_to_catalog(galaxies, catalog, matching_radius=10 * u.arcsec):
#
#     # http://docs.astropy.org/en/stable/coordinates/matchsep.html
#
#     galaxies_coord = SkyCoord(ra=galaxies['ra'] * u.degree, dec=galaxies['dec'] * u.degree)
#     catalog_coord = SkyCoord(ra=catalog['ra'] * u.degree, dec=catalog['dec'] * u.degree)
#     best_match_catalog_index, sky_separation, _ = galaxies_coord.match_to_catalog_sky(catalog_coord)
#
#     galaxies['best_match'] = best_match_catalog_index
#     galaxies['sky_separation'] = sky_separation.to(u.arcsec).value
#     matched_galaxies = galaxies[galaxies['sky_separation'] < matching_radius.value]
#
#     catalog['best_match'] = catalog.index.values
#
#     matched_catalog = pd.merge(matched_galaxies, catalog, on='best_match', how='inner', suffixes=['_subject', ''])
#     unmatched_galaxies = galaxies[galaxies['sky_separation'] >= matching_radius.value]
#
#     return matched_catalog, unmatched_galaxies

def match_galaxies_to_catalog_table(galaxies, catalog, matching_radius=10 * u.arcsec,
                              galaxy_suffix='_subject', catalog_suffix=''):


    galaxies_coord = SkyCoord(ra=galaxies['ra'], dec=galaxies['dec'], unit=u.deg)
    catalog_coord = SkyCoord(ra=catalog['ra'], dec=catalog['dec'], unit=u.deg)

    catalog['best_match'] = np.arange(len(catalog))
    best_match_catalog_index, sky_separation, _ = galaxies_coord.match_to_catalog_sky(catalog_coord)
    galaxies['best_match'] = best_match_catalog_index
    galaxies['sky_separation'] = sky_separation.to(u.arcsec).value
    matched_galaxies = galaxies[galaxies['sky_separation'] < matching_radius.value]

    matched_catalog = table.join(matched_galaxies,
                                 catalog,
                                 keys='best_match',
                                 join_type='inner',
                                 table_names=['{}'.format(galaxy_suffix), '{}'.format(catalog_suffix)],
                                 uniq_col_name='{col_name}{table_name}')
    # correct names not shared
    unmatched_galaxies = galaxies[galaxies['sky_separation'] >= matching_radius.value]
    return matched_catalog, unmatched_galaxies


def match_galaxies_to_catalog_pandas(galaxies, catalog, matching_radius=10 * u.arcsec,
                              galaxy_suffix='_subject', catalog_suffix=''):

    galaxies_coord = SkyCoord(ra=galaxies['ra'].values * u.degree, dec=galaxies['dec'].values * u.degree)
    catalog_coord = SkyCoord(ra=catalog['ra'].values * u.degree, dec=catalog['dec'].values * u.degree)

    catalog['best_match'] = np.arange(len(catalog))
    best_match_catalog_index, sky_separation, _ = galaxies_coord.match_to_catalog_sky(catalog_coord)
    galaxies['best_match'] = best_match_catalog_index
    galaxies['sky_separation'] = sky_separation.to(u.arcsec).value
    matched_galaxies = galaxies[galaxies['sky_separation'] < matching_radius.value]

    matched_catalog = pd.merge(
        matched_galaxies,
        catalog,
        on='best_match',
        how='inner',
        suffixes=['{}'.format(galaxy_suffix), '{}'.format(catalog_suffix)]
    )
    # correct names not shared
    unmatched_galaxies = galaxies[galaxies['sky_separation'] >= matching_radius.value]
    return matched_catalog, unmatched_galaxies


def astropy_table_to_pandas(table):
    """
    Convert astropy table to pandas
    Wrapper for table.to_pandas() that automatically avoids multidimensional columns
    Note that the reverse is already implemented: Table.from_pandas(df)
    Args:
        table (astropy.Table): table to be converted to pandas

    Returns:
        (pd.DataFrame) original table as DataFrame, excluding multi-dim columns
    """
    for col in table.colnames:
        # if it has a shape
        try:
            exists = table[col].shape[1]
        except IndexError:
            print('{} is already one-dim'.format(col))
        else:
            print('converting {}'.format(col))
            col_values = table[col]
            #  convert to string
            col_strings = list(map(lambda x: str(list(x)), col_values))
            # replace original values
            table[col] = col_strings

    df = table.to_pandas()
    return df


def fits_are_identical(fits_a_loc, fits_b_loc):
    """
    Given the location of two fits files, do they have identical pixels?

    Args:
        fits_a_loc (str): location of one fits file
        fits_b_loc (str): location of other fits file

    Returns:
        (bool) True if both fits files have identical pixels (including shape), else False
    """
    pixels_a = fits.open(fits_a_loc)[0].data
    pixels_b = fits.open(fits_b_loc)[0].data
    return np.array_equal(pixels_a, pixels_b)


def cache_table(table_loc, cache_loc, useful_cols, loading_func=Table.read, kwargs=None):
    """
    Save a column subset of astropy.table. This can be read later to save time.
    Args:
        table_loc (str): file location of astropy.table to load
        cache_loc (str): file location to save column subset of astropy.table
        useful_cols (list): of form ['a_column_to_save', ...]
        loading_func (func): function to load table, where first arg is table_loc
        kwargs (dict): (optional) additional keyword arguments for loading_func

    Returns:
        None
    """
    print('Begin caching at {}'.format(current_time()))
    data = loading_func(table_loc, **kwargs)
    print('Table loaded at {}'.format(current_time()))
    data[useful_cols].write(cache_loc, overwrite=True)
    print('Saved to astropy.Table at {}'.format(current_time()))


def current_time():
    return datetime.datetime.now().time()


def current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def load_current_subjects(df, workflow=None, subject_set=None, save_loc=None):
    # if workflow is not None:
    #     df = df[df['workflow_id'] == workflow]
    # if subject_set is not None:
    #     df = df[df['subject_set_id'] == subject_set]
    if df.empty:
        logging.critical('Attempting to load subjects from empty dataframe')
        raise ValueError

    df_with_metadata = split_json_str_to_columns(df, 'metadata')
    df_with_metadata['locations'] = df_with_metadata['locations'].apply(lambda x: json.loads(x)['0'])

    current_hidden_cols = list(filter(lambda x: x.startswith('!'), df_with_metadata.columns.values))
    new_cols = list(map(lambda x: x.strip('!'), current_hidden_cols))  # remove special characters for Talk

    # Renaming breaks. Do manually.
    renaming_list = list(zip(current_hidden_cols, new_cols))
    for n in range(len(current_hidden_cols)):
        old_col = renaming_list[n][0]
        new_col = renaming_list[n][1]
        df_with_metadata[new_col] = df_with_metadata[old_col]
        df_with_metadata = df_with_metadata.drop(old_col, axis=1)
    df_with_metadata = df_with_metadata.dropna(how='all', axis=1)
    # df_renamed = df_with_metadata.rename(columns=dict(zip(current_hidden_cols, new_cols)))

    df_with_metadata = df_with_metadata.rename(columns={'0': 'locations'})
    assert len(df_with_metadata) == len(df)

    if save_loc is not None:
        df_with_metadata.to_csv(save_loc)

    return df_with_metadata


def split_json_str_to_columns(input_df, json_column_name):
    """
    Expand Dataframe column of json string into many columns
    Args:
        input_df (pd.DataFrame): dataframe with json str column
        json_column_name (str): json string column name
    Returns:
        (pd.DataFrame) input dataframe with json column expanded into many columns
    """
    input_df = input_df.reset_index()  # concat cares about the index, but we want a literal join
    json_df = pd.DataFrame(list(input_df[json_column_name].apply(json.loads)))
    new_df = pd.concat([input_df, json_df], axis=1)
    assert len(new_df) == len(input_df)
    return new_df
