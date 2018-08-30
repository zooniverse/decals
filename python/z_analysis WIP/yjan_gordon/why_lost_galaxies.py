import logging
import os

from astropy.table import Table

import shared_utilities
import pandas as pd

from a_download_decals.get_catalogs import selection_cuts
from a_download_decals.get_images import download_images_threaded
from a_download_decals import download_decals_settings
from a_download_decals.get_catalogs import get_joint_nsa_decals_catalog

"""
Yjan Gordon asked for classifications of 805 galaxies. 

790 are in the NSA  (Yjan will look into why these are missing)
790 are in DECALS bricks
782 pass the petrotheta selection cut
745 fits are downloaded (this is a bit concerning - why are some fits missing?)

However, only 693 fits / 745 png pass quality control check
Work around this, and the missing fits, with a fresh download
All 790 galaxies in NSA downloaded and then uploaded to "2018-04-09_yjan_gordon_sdss_sample_790 #20354"
"""


def why_galaxies_not_included(galaxies, nsa, bricks):
    logging.info('Original galaxies: {}'.format(len(galaxies)))
    in_nsa, not_in_nsa = shared_utilities.match_galaxies_to_catalog_table(
        galaxies=galaxies,
        catalog=nsa,
        galaxy_suffix='',
        catalog_suffix='_nsa'
    )
    not_in_nsa_save_loc = 'galaxies_not_in_nsa.csv'
    not_in_nsa.to_pandas().to_csv(not_in_nsa_save_loc)
    logging.info('{} galaxies not in NSA listed in {}'.format(len(not_in_nsa), not_in_nsa_save_loc))

    # Are they in the NSA?
    logging.info('In NSA 1_0_0: {}'.format(len(in_nsa)))
    # Do they pass the selection cuts?
    good_petrotheta = selection_cuts.apply_selection_cuts(in_nsa)
    logging.info('Good petrotheta: {}'.format(len(good_petrotheta)))
    # Are they in decals?
    joint_catalog = get_joint_nsa_decals_catalog.create_joint_catalog(in_nsa, bricks, '5')  # dont apply selection cuts
    logging.info('In DECALS bricks: {}'.format(len(joint_catalog)))
    # Are they successfully downloaded?
    fits_dir = download_decals_settings.fits_dir
    png_dir = download_decals_settings.png_dir
    set_download_directory(joint_catalog, fits_dir, png_dir)
    joint_catalog = download_images_threaded.check_images_are_downloaded(joint_catalog, n_processes=1)
    image_download_stats(joint_catalog)
    return joint_catalog


def download_galaxies_without_cuts(galaxies, nsa):
    # let's redownload all, without filtering - make temp joint catalog
    galaxies_with_nsa, _ = shared_utilities.match_galaxies_to_catalog_table(
        galaxies=galaxies,
        catalog=nsa,
        galaxy_suffix='',
        catalog_suffix='_nsa'
    )
    logging.info('In NSA: {}'.format(len(galaxies_with_nsa)))
    in_decals_bricks = get_joint_nsa_decals_catalog.create_joint_catalog(
        nsa=galaxies_with_nsa,
        bricks=bricks,
        data_release='5')  # dont apply selection cuts
    png_dir = '/Data/repos/decals/python/z_analysis WIP/yjan_gordon/downloaded_without_cuts'
    fits_dir = '/Data/repos/decals/python/z_analysis WIP/yjan_gordon/downloaded_without_cuts'
    for dir in [png_dir, fits_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    joint_catalog = download_images_threaded.download_images_multithreaded(in_decals_bricks, '5', fits_dir, png_dir,
                                                                           overwrite_fits=False, overwrite_png=False)
    logging.info('Downloaded {} galaxies without cuts'.format(joint_catalog))
    image_download_stats(joint_catalog)
    joint_catalog['iauname'] = list(map(lambda x: str(x), joint_catalog['iauname']))  # avoid dtype problems
    joint_catalog_loc = 'gordon_joint_catalog_no_cuts.fits'
    joint_catalog.write(joint_catalog_loc, overwrite=True)
    logging.info('Written new joint catalog to {} for uploader'.format(joint_catalog_loc))


def set_download_directory(joint_catalog, fits_dir, png_dir):
    joint_catalog['fits_loc'] = [
        download_images_threaded.get_loc(fits_dir, galaxy, 'fits') for galaxy in joint_catalog]
    joint_catalog['png_loc'] = [
        download_images_threaded.get_loc(png_dir, galaxy, 'png') for galaxy in joint_catalog]
    # mutates in place


def image_download_stats(catalog):
    existing_fits = catalog[catalog['fits_ready']]
    logging.info('existing fits: {}'.format(len(existing_fits)))
    good_fits = catalog[catalog['fits_filled']]
    logging.info('good fits: {}'.format(len(good_fits)))
    good_png = catalog[catalog['png_ready']]
    logging.info('good png: {}'.format(len(good_png)))


if __name__ == '__main__':

    logging.basicConfig(
        filename='why_lost_galaxies.log',
        filemode='w',
        format='%(asctime)s %(message)s',
        level=logging.INFO)

    gordon_galaxies = Table.from_pandas(pd.read_csv('/data/galaxy_zoo/decals/catalogs/gordon_sdss_sample.csv'))

    nsa_loc = '/Data/repos/decals/nsa_1_0_0_basic_cache.fits'
    nsa = Table.read(nsa_loc)

    bricks_loc = download_decals_settings.bricks_loc
    bricks = Table.read(bricks_loc)

    # why are they missing?
    why_galaxies_not_included(gordon_galaxies, nsa, bricks)

    # download every galaxy in NSA and DECALS to a new directory, without any cuts
    # write joint catalog to disk for later use in uploader
    download_galaxies_without_cuts(gordon_galaxies, nsa)
