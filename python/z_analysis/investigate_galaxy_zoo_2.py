"""
Checks if all DR5 subjects are included in either GZ2 or DR1/DR2
They are - DR5 doesn't contain any new galaxies
"""

import pandas as pd
from astropy.io import fits
from astropy.table import Table

from astropy.coordinates import SkyCoord
from astropy import units as u

import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image

import matplotlib.pyplot as plt

pd.options.display.max_rows = 200
pd.options.display.max_columns = 100


def match_galaxies_to_catalog(galaxies, catalog, matching_radius=10 * u.arcsec):
    # http://docs.astropy.org/en/stable/coordinates/matchsep.html

    galaxies_coord = SkyCoord(ra=galaxies['ra'] * u.degree, dec=galaxies['dec'] * u.degree)
    catalog_coord = SkyCoord(ra=catalog['ra'] * u.degree, dec=catalog['dec'] * u.degree)
    best_match_catalog_index, sky_separation, _ = galaxies_coord.match_to_catalog_sky(catalog_coord)

    galaxies['best_match'] = best_match_catalog_index
    galaxies['sky_separation'] = sky_separation.to(u.arcsec).value
    matched_galaxies = galaxies[galaxies['sky_separation'] < matching_radius.value]

    catalog['best_match'] = catalog.index.values

    matched_catalog = pd.merge(matched_galaxies, catalog, on='best_match', how='inner', suffixes=['_subject', ''])
    unmatched_galaxies = galaxies[galaxies['sky_separation'] >= matching_radius.value]

    return matched_catalog, unmatched_galaxies


def plot_catalog_overlap(catalog_a, catalog_b, legend):

    a_coords = catalog_a[['ra', 'dec']]
    a_coords['catalog'] = legend[0]
    b_coords = catalog_b[['ra', 'dec']]
    b_coords['catalog'] = legend[1]

    df_to_plot = pd.concat([a_coords, b_coords])
    df_to_plot['catalog'] = df_to_plot['catalog'].astype('category')

    canvas = ds.Canvas(plot_width=400, plot_height=400)
    aggc = canvas.points(df_to_plot, 'ra', 'dec', ds.count_cat('catalog'))
    img = tf.shade(aggc)
    export_image(img, 'catalog_overlap')


catalog_dir = '/data/galaxy_zoo/decals/catalogs'

gz_catalog = pd.read_csv('{}/nsa_all_raw_gz_counts_10.0_arcsec.csv'.format(catalog_dir))
print('gz nsa galaxies: {}'.format(len(gz_catalog)))

joint_catalog = Table(fits.getdata('{}/nsa_v1_0_0_decals_dr5.fits'.format(catalog_dir)))
joint_catalog = joint_catalog[['nsa_id', 'ra', 'dec', 'petrotheta']].to_pandas()
print('decals nsa galaxies: {}'.format(len(joint_catalog)))

gz_and_decals = pd.merge(gz_catalog, joint_catalog, on='nsa_id', how='outer')
print('gz and decals: {}'.format(len(gz_and_decals)))

old_galaxies, new_galaxies = match_galaxies_to_catalog(joint_catalog, gz_and_decals)

print(len(old_galaxies))
print(len(new_galaxies))

print(new_galaxies.columns.values)
plot_catalog_overlap(old_galaxies, new_galaxies, ['old', 'new'])

canvas = ds.Canvas(plot_width=400, plot_height=400)
aggc = canvas.points(new_galaxies, 'ra', 'dec')
img = tf.shade(aggc)
export_image(img, 'new_galaxies_in_dr5')

new_galaxies['petrotheta'].hist()
plt.savefig('petrotheta_of_new.png')
plt.clf()
