
from multiprocessing.dummy import Pool as ThreadPool
import functools

import numpy as np
from astropy.io import fits
import astropy.table
from astropy.table import Table
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_nsa_catalog(nsa_catalog_loc, nsa_version):
    '''
    Get the loaded NASA-Sloan Atlas galaxy catalog

    Args:
        nsa_catalog_loc (str): absolute file path to NSA catalog e.g. [dir]/nsa_v_0_1_2.fits
        nsa_version (str): version of NSA catalog e.g v0_1_2. Useful to interpret nsa_id column.

    Returns:
        (astropy.Table) NASA-Sloan Atlas. Each row is a galaxy in SDSS.
    '''

    nsa = astropy.table.Table(fits.getdata(nsa_catalog_loc, 1))
    # Coordinate catalog has uppercase column names. Rename to lowercase match exposure_catalog.
    for colname in nsa.colnames:
        nsa.rename_column(colname, colname.lower())
    nsa.rename_column('nsaid', 'nsa_id')

    nsa['nsa_version'] = nsa_version

    return nsa


def get_decals_bricks(bricks_loc, dr):
    '''
    Return the loaded catalog of DECaLS image bricks
    Catalog must contain brick edges (in ra/dec) and brick exposure counts by band
    Include only bricks with images in r, g, and z-bands.
    No constraints on catalog entry for DR2, oddly.

    Args:
        bricks_loc (str): absolute file path to DECaLS brick catalog e.g. [dir]/decals_dr5.fits
        dr (str): load bricks from (data_release) data release

    Returns:
        (astropy.Table) catalog of RA, Dec edges of DECALS 'brick' tile images in rgz bands
    '''

    bricks_all = astropy.table.Table(fits.getdata(bricks_loc, 1))

    if dr == '1':
        has_g = bricks_all['has_image_g']
        has_r = bricks_all['has_image_r']
        has_z = bricks_all['has_image_z']
        has_catalog = bricks_all['has_catalog']

        bricks = bricks_all[has_g & has_r & has_z & has_catalog]

    elif dr == '2':
        has_g = bricks_all['nobs_max_g'] > 0
        has_r = bricks_all['nobs_max_r'] > 0
        has_z = bricks_all['nobs_max_z'] > 0

        bricks = bricks_all[has_g & has_r & has_z]

    elif dr == '3' or dr == '5':
        has_g = bricks_all['nexp_g'] > 0
        has_r = bricks_all['nexp_r'] > 0
        has_z = bricks_all['nexp_z'] > 0

        bricks = bricks_all[has_g & has_r & has_z]

    else:
        raise Exception('Data release "{}" not recognised'.format(dr))

    assert len(bricks) > len(bricks_all) * 0.1

    return bricks


def find_matching_brick(galaxy, bricks, pbar=None):
    '''
    Find the DECaLS brick covering the (ra, dec) coordinates of an NSA galaxy
    Galaxy coordinates may be part of multiple bricks, but only the first match is returned

    Bricks are roughly 0.25 deg x 0.25 deg on each side
    Three sets of coordinates:
    ra, dec = center of brick
    ra1, dec1 = lower right corner of brick
    ra2, dec2 = upper left corner of brick

    Args:
        galaxy (dict): galaxy row from NASA-Sloan Atlas including RA, DEC
        bricks (astropy.Table): catalog of DECALS bricks, listing RA and DE edges (see above)

    Returns:
        match_count (int) total number of bricks containing the galaxy coordinates
        first_match (int) bricks index of first brick containing the galaxy coordinates
    '''

    ragal, decgal = galaxy['ra'], galaxy['dec']

    # Find boolean array of bricks that match in RA
    ramatch = (bricks['ra1'] < ragal) & (bricks['ra2'] >= ragal)

    # Find boolean array of bricks that match in dec
    decmatch = (bricks['dec1'] < decgal) & (bricks['dec2'] >= decgal)

    # boolean array of bricks that match in both RA and dec
    coomatch = (ramatch & decmatch)
    match_count = coomatch.sum()
    first_match = coomatch.argmax()

    if pbar:
        pbar.update()

    return match_count, first_match


def create_joint_catalog(nsa, bricks, data_release, run_to=None, visualise=False):
    '''
    Create a matched catalogue of all NSA sources that have grz imaging in DECaLS
    Selection criteria (currently petrosian radius > 3) are NOT applied here

    Args:
        nsa (astropy.Table): NSA catalog of SDSS galaxies
        bricks (astropy.Table): catalog of DECALS imaging bricks
        data_release (str): DECALS data release version e.g. '2'
        run_to (int): nsa galaxies to match. If None, matches all
        visualise (bool): if True, plot and save sky footprint of NSA catalog

    Returns:
        (astropy.Table) of format [{NSA galaxy, NSA details, DECALS brick with that galaxy}]
    '''

    # Make this routine somewhat quicker by first eliminating everything in the NSA catalog
    # outside the observed RA/dec range of the DECaLS bricks.
    nsa_in_decals_area = filter_nsa_catalog_to_approximate_sky_area(nsa, bricks, visualise=visualise)

    nsa_to_match = nsa_in_decals_area[:run_to]

    # For every galaxy in the NSA catalog, if it is in DECALS RA/DEC window, find which brick(s) it is in
    pbar = tqdm(total=len(nsa_to_match), unit=' galaxies checked')

    match_params = {
        'bricks': bricks,
        'pbar': pbar
    }
    find_matching_brick_partial = functools.partial(find_matching_brick, **match_params)

    pool = ThreadPool(10)
    # must be an ordered map! relies on nsa index
    results = np.array(pool.map(find_matching_brick_partial, nsa_to_match))
    pbar.close()
    pool.close()
    pool.join()
    # match count is number of bricks with galaxy n, for all galaxies
    # first match is the first index of bricks containing galaxy n, for all galaxies
    match_count, first_match = results[:, 0], results[:, 1]

    # filter matches and nsa table to only galaxies which are matched to DECALS bricks
    has_match = match_count > 0
    match_count = match_count[has_match]
    first_match = first_match[has_match]
    nsa_decals = nsa_to_match[has_match]  # all nsa galaxies imaged by decals - will have decals data added

    # ought to have as many galaxies shared between nsa and decals as decals brick indexes for nsa galaxies
    assert len(nsa_decals) == len(first_match), \
        "Length of joint_catalog ({0}) and bricks_indices ({1}) must match".format(len(nsa_decals), len(first_match))

    matched_bricks = Table(bricks[first_match])

    assert len(nsa_decals) == len(matched_bricks)

    # add the bricks data into the joint_catalog table (manual merge)
    nsa_decals_bricks = astropy.table.hstack([nsa_decals, matched_bricks])
    assert len(nsa_decals_bricks) == len(matched_bricks)

    print('{0:6d} galaxies match between NASA-Sloan Atlas and DECaLS DR{1}'.format(has_match.sum(), data_release))
    print('{0:6d} galaxies had matches in more than one brick'.format((match_count > 1).sum()))

    return nsa_decals


def filter_nsa_catalog_to_approximate_sky_area(nsa, bricks, visualise=False):
    """
    DECALS is only in a well-defined portion of sky (which depends on the data release version). Filter the NSA catalog
    so that it only includes galaxies in that approximate area. This saves time matching later.

    Args:
        nsa (astropy.Table): NSA catalog of SDSS galaxies
        bricks (astropy.Table): catalog of DECALS imaging bricks
        visualise (bool): if True, plot and save sky footprint of NSA catalog

    Returns:

        (astropy.Table) NSA catalog filtered to galaxies within the approximate sky area imaged by DECALS

    """

    if visualise:
        fig, ((ul, ur), (ll, lr)) = plt.subplots(2, 2)
        ul.hist(bricks['dec'])
        ul.set_title('brick dec')
        ur.hist(nsa['dec'])
        ur.set_title('nsa dec')
        ll.hist(bricks['ra'])
        ll.set_title('brick ra')
        lr.hist(nsa['ra'])
        lr.set_title('nsa ra')
        plt.tight_layout()
        plt.savefig('nsa_catalog_sky_coverage.png')

    brick_maxdec = max(bricks['dec2'])
    brick_mindec = min(bricks['dec1'])

    # ra spans 0 through 360, do not filter
    declim = (nsa['dec'] >= brick_mindec) & (nsa['dec'] <= brick_maxdec)  # approximately -25 to +30 degrees

    nsa_in_decals_area = nsa[declim]

    return nsa_in_decals_area
