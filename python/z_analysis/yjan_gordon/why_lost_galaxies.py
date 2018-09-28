import logging
import os
from collections import Counter

from astropy import table
from astropy.table import Table

from shared_astro_utils import matching_utils
import pandas as pd

from a_download_decals.get_catalogs import selection_cuts
from a_download_decals.get_images import download_images_threaded
from a_download_decals import download_decals_settings
from a_download_decals.get_catalogs import get_joint_nsa_decals_catalog

"""
Initially....
Yjan Gordon asked for classifications of 805 galaxies. 

790 are in the NSA  (Yjan will look into why these are missing)
790 are in DECALS bricks
782 pass the petrotheta selection cut
745 fits are downloaded (this is a bit concerning - why are some fits missing?)

However, only 693 fits / 745 png pass quality control check
Work around this, and the missing fits, with a fresh download
All 790 galaxies in NSA downloaded and then uploaded to "2018-04-09_yjan_gordon_sdss_sample_790 #20354"


Second batch...
12th Sept Yjan sent over a further 1100 galaxies to classify early


"""

def why_galaxies_not_included(galaxies, nsa, bricks):
    logging.info('Original galaxies: {}'.format(len(galaxies)))
    in_nsa_maybe_duplicate, not_in_nsa = matching_utils.match_galaxies_to_catalog_table(
        galaxies=galaxies,
        catalog=nsa,
        galaxy_suffix='',
        catalog_suffix='_nsa'
    )
    not_in_nsa_save_loc = 'galaxies_not_in_nsa.csv'
    not_in_nsa.to_pandas().to_csv(not_in_nsa_save_loc)
    logging.info('{} galaxies not in NSA listed in {}'.format(len(not_in_nsa), not_in_nsa_save_loc))
    # Are they duplicates?
    in_nsa = table.unique(in_nsa_maybe_duplicate, keep='first', keys='sdss_id')
    logging.info('Duplicate NSA cross-matches, selecting {} first matches only'.format(len(in_nsa_maybe_duplicate) - len(in_nsa)))
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


def download_galaxies_without_cuts(galaxies, nsa, joint_loc, png_dir, fits_dir):
    """[summary]
    
    Args:
        galaxies ([type]): [description]
        nsa ([type]): [description]
        joint_loc ([type]): save location for new joint catalog
    """

    # let's redownload all, without filtering - make temp joint catalog
    galaxies_with_nsa_maybe_duplicate, _ = matching_utils.match_galaxies_to_catalog_table(
        galaxies=galaxies,
        catalog=nsa,
        galaxy_suffix='',
        catalog_suffix='_nsa'
    )
    # if duplicate match to NSA catalog, pick the first
    galaxies_with_nsa = table.unique(galaxies_with_nsa_maybe_duplicate, keys='iauname', keep='first')
    logging.warning('Dropped {} galaxies that matched to the same NSA entry'.format(len(galaxies_with_nsa_maybe_duplicate) - len(galaxies_with_nsa)))
    assert len(table.unique(galaxies_with_nsa, keys='iauname')) == len(galaxies_with_nsa)

    logging.info('In NSA: {}'.format(len(galaxies_with_nsa)))
    in_decals_bricks = get_joint_nsa_decals_catalog.create_joint_catalog(
        nsa=galaxies_with_nsa,
        bricks=bricks,
        data_release='5')  # dont apply selection cuts
    assert len(table.unique(in_decals_bricks, keys='iauname')) == len(in_decals_bricks)

    for dir in [png_dir, fits_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    joint_catalog = download_images_threaded.download_images_multithreaded(
        in_decals_bricks, 
        '5', 
        fits_dir, 
        png_dir,
        overwrite_fits=False,
        overwrite_png=False
    )
    logging.info('Downloaded {} galaxies without cuts'.format(joint_catalog))
    image_download_stats(joint_catalog)
    joint_catalog['iauname'] = list(map(lambda x: str(x), joint_catalog['iauname']))  # avoid dtype problems
    joint_catalog.write(joint_loc, overwrite=False)  # not allowed to overwrite, for safety
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

    # logging.basicConfig(
    #     filename='/Data/repos/decals/python/z_analysis/yjan_gordon/why_lost_galaxies_second_sample.log',
    #     filemode='w',
    #     format='%(asctime)s %(message)s',
    #     level=logging.INFO)

    # initial
    # gordon_galaxies = Table.from_pandas(pd.read_csv('/data/galaxy_zoo/decals/catalogs/gordon_sdss_sample.csv'))
    # joint_catalog_loc = 'gordon_joint_catalog_no_cuts.fits'
    # png_dir = '/Data/repos/decals/python/z_analysis/yjan_gordon/downloaded_without_cuts'
    # fits_dir = '/Data/repos/decals/python/z_analysis/yjan_gordon/downloaded_without_cuts'

    # sample 2
    gordon_galaxies = Table.from_pandas(pd.read_csv('/data/galaxy_zoo/decals/catalogs/gordon_sdss_sample_2.csv'))
    for col in gordon_galaxies.colnames:
        gordon_galaxies[col].name = col.lower()
    joint_catalog_loc = 'gordon_joint_catalog_no_cuts_second.fits'
    png_dir = '/Data/repos/decals/python/z_analysis/yjan_gordon/downloaded_without_cuts_sample_2'
    fits_dir = '/Data/repos/decals/python/z_analysis/yjan_gordon/downloaded_without_cuts_sample_2'


    # begin
    nsa_loc = '/Data/repos/decals/nsa_1_0_0_basic_cache.fits'
    nsa = Table.read(nsa_loc)

    bricks_loc = download_decals_settings.bricks_loc
    bricks = Table.read(bricks_loc)

    
    # why are they missing?
    unique_galaxies = table.unique(gordon_galaxies, keys='sdss_id')
    if len(unique_galaxies) != len(gordon_galaxies):
        counter = Counter(gordon_galaxies['sdss_id'])
        logging.warning('Warning - duplicate ids provided:')
        for sdss_id, count in counter.items():
            if count > 1:
                logging.warning('sdss_id: {}, count: {}'.format(sdss_id, count))
    unique_galaxies.to_pandas().to_csv('/Data/repos/decals/python/z_analysis/gordon_galaxies_sample_2_unique.csv')
    # why_galaxies_not_included(unique_galaxies, nsa, bricks)

    # download every galaxy in NSA and DECALS to a new directory, without any cuts
    # write joint catalog to disk for later use in uploader
    # download_galaxies_without_cuts(unique_galaxies, nsa, joint_catalog_loc, png_dir, fits_dir)
