# Find entries in the NASA-Sloan Atlas (NSA) that have a brick with images in Dark Energy Camera Legacy Survey (DECaLS)

import warnings

import pandas as pd
from astropy.io import fits
from astropy.table import Table

from a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import create_joint_catalog, get_nsa_catalog, get_decals_bricks
from a_download_decals.get_catalogs.selection_cuts import apply_selection_cuts
from a_download_decals.get_images.download_images_threaded import download_images_multithreaded
from a_download_decals.setup.join_brick_tables import merge_bricks_catalogs
import a_download_decals.download_decals_settings as settings


def setup_tables(s):
    """
    Generate the 'bricks' and 'previous subjects' data tables used in main program.
    Only needs to be run once after downloading the required files.

    Args:
        s (Settings) object wrapper for user-specified settings

    Returns:
        None
    """
    if s.data_release == '3' or s.data_release == '5':
        coordinate_catalog = Table(fits.getdata(s.brick_coordinates_loc, 1))
        exposure_catalog = Table(fits.getdata(s.brick_exposures_loc, 1))
        bricks_catalog = merge_bricks_catalogs(coordinate_catalog, exposure_catalog)
        bricks_catalog.write(s.bricks_loc, overwrite=True)

    else:
        warnings.warn('Data release "{}" does not require joining brick tables - skipping'.format(s.data_release))


def get_decals(nsa=None, bricks=None, s=None):
    """
    Find NSA galaxies imaged by DECALS. Download fits. Create RGB pngs. Return catalog of new galaxies.

    Args:
        nsa (astropy.Table): catalog of NSA galaxies
        bricks (astropy.Table): catalog of DECALS bricks, including center, edges and exposure counts
        previous_subjects (pd.DataFrame):
        s (Settings): object wrapper for user-specified behaviour

    Returns:
        (pd.DataFrame) catalog of DECaLS galaxies not previously classified in Galaxy Zoo
    """

    include_names = [
        'iauname',
        'nsa_id',
        'ra',
        'dec',
        'petrotheta',
        'petroth50',
        'petroth90',
        'z',
        'nsa_version'
    ]

    if s.new_catalog:
        print('get new catalog')
        nsa_after_cuts = apply_selection_cuts(nsa)
        joint_catalog = create_joint_catalog(nsa_after_cuts, bricks, s.nsa_version, run_to=s.run_to)
        joint_catalog = joint_catalog[include_names]
        print('writing new catalog')
        joint_catalog.write(s.joint_catalog_loc, overwrite=True)
    else:
        print('get joint catalog')
        joint_catalog = Table.read(s.joint_catalog_loc)[include_names]

    if s.new_images:
        print('get new images')
        joint_catalog = download_images_multithreaded(
            joint_catalog[:s.run_to],
            s.data_release,
            s.fits_dir,
            s.png_dir,
            overwrite_fits=s.overwrite_fits,
            overwrite_png=s.overwrite_png)

    return joint_catalog


def main():
    """
    Create the NSA-DECaLS-GZ catalog, download fits, produce png, and identify new subjects

    Returns:
        None
    """

    # specify setup options
    new_bricks_table = False  # if DR3+, run this on first use.

    # Setup tasks generate the 'bricks' data table used later.
    # They need only be completed once after downloading the required files
    if new_bricks_table:
        setup_tables(settings)
        print('setup complete')

    # specify execution options
    settings.new_catalog = True
    settings.new_images = True
    settings.overwrite_fits = False
    settings.overwrite_png = False
    settings.run_to = None

    if settings.new_catalog:
        nsa = get_nsa_catalog(settings.nsa_catalog_loc, settings.nsa_version)
        print('nsa loaded')
        bricks = get_decals_bricks(settings.bricks_loc, settings.data_release)
        print('bricks loaded')
    else:
        nsa = None
        bricks = None

    joint_catalog = get_decals(nsa, bricks, settings)
    joint_catalog.write(settings.upload_catalog_loc, overwrite=True)


if __name__ == '__main__':
    main()
