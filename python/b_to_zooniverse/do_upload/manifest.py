import ast
import os
import functools
from multiprocessing.dummy import Pool as ThreadPool
import logging

import numpy as np
import astropy.table
import pandas as pd
from panoptes_client import Panoptes, Project, SubjectSet, Subject
from tqdm import tqdm

from b_to_zooniverse.do_upload.make_decals_metadata import get_key_astrophysical_columns
from b_to_zooniverse.to_zooniverse_settings import zooniverse_login_loc
from shared_astro_utils import time_utils


def create_manifest_from_calibration_catalog(catalog, image_columns):
    """
    Convert manifest to look like a joint catalog (one row per galaxy, png_loc column), then upload as normal
    Args:
        catalog (astropy.Table):
        image_columns (list): strings of column names with locations of possible images e.g. [dr2_png_loc, etc]

    Returns:

    """
    fake_joint_catalog = convert_calibration_to_joint_catalog(catalog, image_columns)

    return create_manifest_from_joint_catalog(fake_joint_catalog)


def convert_calibration_to_joint_catalog(calibration_catalog, image_columns):
    """
    Expand calibration catalog to have one row per image, image under 'png_loc'.
    Record which image processing was used under 'selected_image'.
    Args:
        calibration_catalog (astropy.Table): expertly-classified galaxies with multiple calibration images
        image_columns (list): strings of column names with locations of possible images e.g. [dr2_png_loc, etc]

    Returns:
        (pd.DataFrame) calibration catalog to upload, one galaxy per row, 'png_loc' with selected image
    """
    all_calibration_sets = []
    for image_col in image_columns:
        calibration_set = calibration_catalog.copy()
        calibration_set['png_loc'] = calibration_set[image_col]
        calibration_set['selected_image'] = image_col

        all_calibration_sets.append(calibration_set)

    return astropy.table.vstack(all_calibration_sets)


def create_manifest_from_joint_catalog(catalog):
    """
    Create dict of files and metadata
    Catalog including 'png_loc' and key astro data, one galaxy per row
    Args:
        catalog (astropy.Table): catalog to upload

    Returns:
        (dict) of form {png_loc: img.png, key_data: {metadata_col: metadata_value}}
    """
    logging.debug(catalog)
    key_data = get_key_astrophysical_columns(catalog)

    # there's a weird bug in astropy where certain strings are converted to bytes when added to pandas
    # nsa_version '1_0_0' becomes b'1_0_0'
    # TODO raise an astropy issue about this - or better, fix it!
    nsa_version_data = key_data['nsa_version']
    key_data = key_data.to_pandas()  # becomes bytes if included
    key_data['nsa_version'] = nsa_version_data  # becomes bytes even when manually placed!
    key_data['nsa_version'] = key_data['nsa_version'].str.decode("utf-8")  # convert back to string

    # np.nan cannot be handled by JSON encoder. Convert to flag value of -999
    key_data = key_data.applymap(replace_nan_with_flag)
    # bytes cannot be handled by JSON encoder. Convert to string
    key_data = key_data.applymap(replace_bytes_with_str)

    # calibration catalog can have 'selected image' column
    try:
        key_data['selected_image'] = catalog['selected_image']
    except KeyError:
        pass

    key_data['decals_search'] = key_data.apply(
        lambda galaxy: coords_to_decals_skyviewer(galaxy['ra'], galaxy['dec']),
        axis=1)
    key_data['sdss_search'] = key_data.apply(
        lambda galaxy: coords_to_sdss_navigate(galaxy['ra'], galaxy['dec']),
        axis=1)
    key_data['panstarrs_dr1_search'] = key_data.apply(
        lambda galaxy: coords_to_panstarrs(galaxy['ra'], galaxy['dec']),
        axis=1)
    key_data['simbad_search'] = key_data.apply(
        lambda galaxy: coords_to_simbad(galaxy['ra'], galaxy['dec'], search_radius=10.),
        axis=1)
    key_data['nasa_ned_search'] = key_data.apply(
        lambda galaxy: coords_to_ned(galaxy['ra'], galaxy['dec'], search_radius=10.),
        axis=1)
    key_data['vizier_search'] = key_data.apply(
        lambda galaxy: coords_to_vizier(galaxy['ra'], galaxy['dec'], search_radius=10.),
        axis=1)

    markdown_text = {
        'decals_search': 'Click to view in DECALS',
        'sdss_search': 'Click to view in SDSS',
        'panstarrs_dr1_search': 'Click to view in PANSTARRS DR1',
        'simbad_search': 'Click to search SIMBAD',
        'nasa_ned_search': 'Click to search NASA NED',
        'vizier_search': 'Click to search VizieR'
    }
    for link_column, link_text in markdown_text.items():
        key_data[link_column] = key_data[link_column].apply(
            lambda url: wrap_url_in_new_tab_markdown(url=url, display_text=link_text))

    # rename all key data columns to appear only in Talk by prepending with '!'
    current_columns = key_data.columns.values
    prepended_columns = ['!' + col for col in current_columns]
    key_data = key_data.rename(columns=dict(zip(current_columns, prepended_columns)))

    key_data['metadata_message'] = 'Metadata is available in [Talk](+tab+https://www.zooniverse.org/projects/zookeeper/galaxy-zoo/talk)'
    key_data['#upload_date'] = time_utils.current_date()  # not shown to users

    # create the manifest structure that Panoptes Python client expects
    key_data_as_dicts = key_data.apply(lambda x: x.to_dict(), axis=1).values

    png_locs = pd.Series(catalog['png_loc']).values

    data = zip(png_locs, key_data_as_dicts)
    manifest = list(map(lambda x: {'png_loc': x[0], 'key_data': x[1]}, data))

    return manifest


def upload_manifest_to_galaxy_zoo(subject_set_name, manifest, galaxy_zoo_id='5733', n_processes=10):
    """
    Save manifest (set of galaxies with metadata prepared) to Galaxy Zoo

    Args:
        subject_set_name (str): name for subject set
        manifest (list): containing dicts of form {png_loc: img.png, key_data: {metadata_col: metadata_value}}
        galaxy_zoo_id (str): panoptes project id e.g. '5733' for Galaxy Zoo, '6490' for mobile
        n_processes (int): number of processes with which to upload galaxies in parallel

    Returns:
        None
    """
    if 'TEST' in subject_set_name:
        logging.warning('Testing mode detected - not uploading!')
        return manifest

    if galaxy_zoo_id == '5733':
        logging.info('Uploading to Galaxy Zoo project 5733')
    elif galaxy_zoo_id == '6490':
        logging.info('Uploading to mobile app project 6490')
    else:
        logging.info('Uploading to unknown project {}'.format(galaxy_zoo_id))

    # Important - don't commit the password!
    zooniverse_login = read_data_from_txt(zooniverse_login_loc)
    Panoptes.connect(**zooniverse_login)

    galaxy_zoo = Project.find(galaxy_zoo_id)

    subject_set = SubjectSet()

    subject_set.links.project = galaxy_zoo
    subject_set.display_name = subject_set_name
    subject_set.save()

    pbar = tqdm(total=len(manifest), unit=' subjects uploaded')

    save_subject_params = {
        'project': galaxy_zoo,
        'pbar': pbar
    }
    save_subject_partial = functools.partial(save_subject, **save_subject_params)
    pool = ThreadPool(n_processes)
    new_subjects = pool.map(save_subject_partial, manifest)
    pbar.close()
    pool.close()
    pool.join()

    # new_subjects = []
    # for subject in manifest:
    #     print(subject)
    #     new_subjects.append(save_subject_partial(subject))

    subject_set.add(new_subjects)

    return manifest  # for debugging only


def save_subject(manifest_item, project, pbar=None):
    """

    Add manifest item to project. Note: follow with subject_set.add(subject) to associate with subject set.
    Args:
        manifest_item (dict): of form {png_loc: img.png, key_data: some_data_dict}
        project (str): project to upload subject too e.g. '5773' for Galaxy Zoo
        pbar (tqdm.tqdm): progress bar to update. If None, no bar will display.

    Returns:
        None
    """
    subject = Subject()

    subject.links.project = project
    assert os.path.exists(manifest_item['png_loc'])
    subject.add_location(manifest_item['png_loc'])
    subject.metadata.update(manifest_item['key_data'])

    subject.save()

    if pbar:
        pbar.update()

    return subject


def read_data_from_txt(file_loc):
    """
    Read and evaluate a python data structure saved as a txt file.
    Args:
        file_loc (str): location of file to read

    Returns:
        data structure contained in file
    """
    with open(file_loc, 'r') as f:
        s = f.read()
        return ast.literal_eval(s)


def replace_nan_with_flag(x):
    """
    For any x, if x is nan or masked, replace with -999
    Args:
        x (Any): input of unknown type to be checked

    Returns:
        (float): -999 if x is of nan or masked, x if not
    """
    try:
        if np.isnan(x) or np.isinf(x):
            return -999.
        else:
            return x
    except TypeError:  # not a numpy-supported data type e.g. string, therefore can't be nan
        return x


def replace_bytes_with_str(x):
    """
    For any x, if x is nan or masked, replace with -999
    Args:
        x (Any): input of unknown type to be checked

    Returns:
        (float): -999 if x is of nan or masked, x if not
    """
    if type(x) is bytes:
        return x.decode('utf-8')
    else:
        return x


def coords_to_simbad(ra, dec, search_radius):
    """
    Get SIMBAD search url for objects within search_radius of ra, dec coordinates.
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees
        search_radius (float): search radius around ra, dec in arcseconds

    Returns:
        (str): SIMBAD database search url for objects at ra, dec
    """
    return 'http://simbad.u-strasbg.fr/simbad/sim-coo?Coord={0}+%09{1}&CooFrame=FK5&CooEpoch=2000&CooEqui=2000&CooDefinedFrames=none&Radius={2}&Radius.unit=arcmin&submit=submit+query&CoordList='.format(ra, dec, search_radius)


def coords_to_decals_skyviewer(ra, dec):
    """
    Get decals_skyviewer viewpoint url for objects within search_radius of ra, dec coordinates. Default zoom.
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees

    Returns:
        (str): decals_skyviewer viewpoint url for objects at ra, dec
    """
    return 'http://www.legacysurvey.org/viewer?ra={}&dec={}&zoom=15&layer=decals-dr5'.format(ra, dec)


def coords_to_sdss_navigate(ra, dec):
    """
    Get sdss navigate url for objects within search_radius of ra, dec coordinates. Default zoom.
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees

    Returns:
        (str): sdss navigate url for objects at ra, dec
    """
    # skyserver.sdss.org really does skip the wwww, but needs http or link keeps the original Zooniverse root
    return 'http://skyserver.sdss.org/dr14/en/tools/chart/navi.aspx?ra={}&dec={}&scale=0.1&width=120&height=120&opt='.format(ra, dec)


def coords_to_ned(ra, dec, search_radius):
    """
    Get NASA NED search url for objects within search_radius of ra, dec coordinates.
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees
        search_radius (float): search radius around ra, dec in arcseconds

    Returns:
        (str): SIMBAD database search url for objects at ra, dec
    """
    ra_string = '{:3.8f}d'.format(ra)
    dec_string = '{:3.8f}d'.format(dec)
    search_radius_arcmin = search_radius / 60.
    return 'https://ned.ipac.caltech.edu/cgi-bin/objsearch?search_type=Near+Position+Search&in_csys=Equatorial&in_equinox=J2000.0&lon={}&lat={}&radius={}&hconst=73&omegam=0.27&omegav=0.73&corr_z=1&z_constraint=Unconstrained&z_value1=&z_value2=&z_unit=z&ot_include=ANY&nmp_op=ANY&out_csys=Equatorial&out_equinox=J2000.0&obj_sort=Distance+to+search+center&of=pre_text&zv_breaker=30000.0&list_limit=5&img_stamp=YES'.format(ra_string, dec_string, search_radius_arcmin)


def coords_to_vizier(ra, dec, search_radius):
    """
    Get vizier search url for objects within search_radius of ra, dec coordinates.
    Include radius from search target, sort by radius from search target.
    http://vizier.u-strasbg.fr/doc/asu-summary.htx
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees
        search_radius (float): search radius around ra, dec in arcseconds

    Returns:
        (str): vizier url for objects at ra, dec
    """
    return 'http://vizier.u-strasbg.fr/viz-bin/VizieR?&-c={},{}&-c.rs={}&-out.add=_r&-sort=_r'.format(
        ra, dec, search_radius)


def coords_to_panstarrs(ra, dec):
    """
    Get panstarrs dr1 cutout url at ra, dec coordinates.
    http://ps1images.stsci.edu/cgi-bin/ps1cutouts
    Args:
        ra (float): right ascension in degrees
        dec (float): declination in degrees

    Returns:
        (str): cutout url for objects at ra, dec
    """
    return 'http://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos={}{:+f}&filter=color&filter=g&filter=r&filter=i&filter=z&filter=y&filetypes=stack&auxiliary=data&size=240&output_size=0&verbose=0&autoscale=99.500000&catlist='.format(
        ra, dec)


def wrap_url_in_new_tab_markdown(url, display_text):
    return '[{}](+tab+{})'.format(display_text, url)
