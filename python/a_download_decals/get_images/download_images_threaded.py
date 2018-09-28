import functools
import os
import warnings
import multiprocessing
import subprocess

import numpy as np
from numba import jit
from astropy.io import fits
from tqdm import tqdm
from PIL import Image

from a_download_decals.get_images.image_utils import dr2_style_rgb


def download_images_multithreaded(catalog, data_release, fits_dir, png_dir, overwrite_fits, overwrite_png, n_processes=10):
    '''
    Download fits of catalog, create png images. Update catalog with fits and png locations. Run multithreaded.

    Args:
        catalog (astropy.Table): catalog of NSA galaxies and DECALS bricks
        data_release (str): DECALS data release e.g. '3'
        fits_dir (str): directory to save fits files
        png_dir (str): directory to save png files
        overwrite_fits (bool): if True, force new fits download.
        overwrite_png (bool): if True, force new png download.
        n_processes (int): number of processes to run in parallel for download and checking of fits
    Returns:
        (astropy.Table) catalog with new columns for fits/png locations and quality checks
    '''

    # Table does not support .apply - use list comprehension instead
    catalog['fits_loc'] = [get_loc(fits_dir, catalog[index], 'fits') for index in range(len(catalog))]
    catalog['png_loc'] = [get_loc(png_dir, catalog[index], 'png') for index in range(len(catalog))]
    assert len(catalog['fits_loc']) == len(set(catalog['fits_loc']))  # no duplicates allowed

    download_params = {
        'data_release': data_release,
        'overwrite_fits': overwrite_fits,
        'overwrite_png': overwrite_png,
    }
    download_images_partial = functools.partial(download_images, **download_params)

    manual_chunksize = 20000
    remaining_catalog = catalog.copy()
    while True:
        print('Images left: {}'.format(len(remaining_catalog)))
        chunk = remaining_catalog[-manual_chunksize:]
        remaining_catalog = remaining_catalog[:-manual_chunksize]
        pool = multiprocessing.Pool(n_processes)
        list(tqdm(
            pool.imap(download_images_partial, chunk),  total=len(chunk),
            unit='downloaded'))
        pool.close()
        pool.join()
        if len(remaining_catalog) == 0:
            break

    catalog = check_images_are_downloaded(catalog, n_processes=n_processes)

    print("\n{} total galaxies".format(len(catalog)))
    print("{} fits are downloaded".format(np.sum(catalog['fits_ready'])))
    print("{} png generated".format(np.sum(catalog['png_ready'])))
    print("{} fits have many bad pixels".format(len(catalog) - np.sum(catalog['fits_filled'])))

    return catalog


def download_images(galaxy,
                    data_release,
                    overwrite_fits=False,
                    overwrite_png=False,
                    max_attempts=5,
                    min_pixelscale=0.1,
                    png_size=424,
                    lazy_checking=False):
    """
    Download a multi-plane FITS image from the DECaLS skyserver
    Write multi-plane FITS images to separate files for each band
    Default arguments are used due to pool.map(download_images, nsa), no more args. Can fix.
    Args:
        galaxy (astropy.TableRow): catalog entry of galaxy to download
        data_release (str): DECALS data release e.g. '2'
        overwrite_fits (bool): download fits even if fits file already exists in target location
        overwrite_png (bool): download png even if png file already exists in target location
        pbar (tqdm): progress bar shared between processes, to be updated. If None, no progress bar will be shown.
        max_attempts (int): max number of fits download attempts per file
        min_pixelscale(float): minimum pixel scale to request from server, if object is tiny
        lazy_checking (bool): if True, attempt to open .fits files. Else, only check if .fits exists

    Returns:
        None
    """

    try:

        pixscale = max(min(galaxy['petroth50'] * 0.04, galaxy['petroth90'] * 0.02), min_pixelscale)

        # For convenience
        fits_loc = galaxy['fits_loc']
        png_loc = galaxy['png_loc']

        # Download multi-band fits images
        if lazy_checking:   # only check if file exists, for speed
            get_new_fits = (not os.path.exists(fits_loc)) or overwrite_fits
        else:
            get_new_fits = not fits_downloaded_correctly(fits_loc) or overwrite_fits

        if get_new_fits:
            attempt = 0
            while attempt < max_attempts:
                try:
                    download_fits_cutout(fits_loc, data_release, galaxy['ra'], galaxy['dec'], pixscale, 512)
                    assert fits_downloaded_correctly(fits_loc)
                    break
                except Exception as err:
                    print(err, 'on galaxy {}, attempt {}'.format(galaxy['iauname'], attempt), flush=True)
                    attempt += 1
                if attempt == max_attempts:
                    warnings.warn('Failed to download {} after three attempts. No fits at {}'.format(
                        galaxy['iauname'], galaxy['fits_loc']))

        if not os.path.exists(png_loc) or overwrite_png:
            try:
                # Create artistic png from the new FITS
                make_png_from_fits(fits_loc, png_loc, png_size)
            except:
                print('Error creating png from {}'.format(fits_loc))

    except Exception as err:  # necessary to (sometimes) avoid threads dying silently
        print('FATAL THREAD ERROR: {}'.format(err))
        exit(1)


def fits_downloaded_correctly(fits_loc):
    """
    Is there a readable fits image at fits_loc?
    Does NOT check for bad pixels

    Args:
        fits_loc (str): location of fits file to open

    Returns:
        (bool) True if file at fits_loc is readable, else False
    """

    try:
        img, _ = fits.getdata(fits_loc, 0, header=True)
        return True
    except Exception:  # image fails to open
        return False


def get_loc(dir, galaxy, extension):
    '''
    Get full path where image file of galaxy should be saved, given directory
    Defines standard location convention for images
    Places into subdirectories based on first 4 characters of iauname to avoid filesystem problems with 300k+ files

    Args:
        dir (str): target directory for image files
        galaxy (astropy.TableRecord): row of NSA/DECALS catalog with galaxy info e.g. name
        extension (str): file extension to use e.g. fits, png

    Returns:
        (str) full path of where galaxy file should be saved
    '''
    target_dir = '{}/{}'.format(dir, galaxy['iauname'][:4])
    if not os.path.isdir(target_dir):  # place each galaxy in a directory with first 3 letters of iauname (i.e. RA)
        try:
            os.mkdir(target_dir)
        except FileExistsError:  # when running multithreaded, another thread could make directory between checks
            if os.path.isdir(target_dir):
                pass
    return '{}/{}.{}'.format(target_dir, galaxy['iauname'], extension)


def shell_command(cmd, executable=None, timeout=60):
    result = subprocess.Popen(cmd, shell=True, executable=executable)
    name = result.pid
    try:
        result.wait(timeout=timeout)
    except Exception as err:
        result.kill()
        print('{} killed due to {}'.format(name, err))
    return result


def download_fits_cutout(fits_loc, data_release, ra=114.5970, dec=21.5681, zoomed_pixscale=0.262, max_size=512):
    '''
    Retrieve fits image from DECALS server and save to disk

    Args:
        fits_loc (str): location to save file, excluding type e.g. /data/fits/test_image.fits
        ra (float): right ascension (center)
        dec (float): declination (center)
        zoomed_pixscale (float):  arcseconds per pixel requested. Native pixscale is 0.262
        max_size (int): maximum pixels to download before increasing zoomed_pixscale

    Returns:
        None
    '''

    url = get_download_url(ra, dec, zoomed_pixscale, max_size, data_release, img_format='fits')

    wget_location = '/opt/local/bin/wget'
    try:
        if os.environ['ON_TRAVIS'] == 'True':
            wget_location = 'wget'
    except KeyError:
        pass
    download_command = '{} --tries=5 --no-verbose -q -O "{}" "{}"'.format(wget_location, fits_loc, url)
    _ = shell_command(download_command)


def get_download_url(ra, dec, zoomed_pixscale, max_size, data_release, img_format):
    """
    Generate the DECALS cutout service URL used to download each image, as either png or jpeg
    Args:
        ra (float): right ascension of galaxy
        dec (float): declination of galaxy
        zoomed_pixscale (float): arcseconds per pixel requested. Native pixscale is 0.262.
        max_size (int): maximum pixels to download before increasing zoomed_pixscale
        data_release (str): DECALS data release to source image from
        img_format (str): image format to download. 'fits' or 'jpg'

    Returns:
        (str): url to download galaxy in requested size/format
    """
    # TODO combine these historical size and zoomed pixscale into a new, meaningful measure. pixscale -> arcsecs
    historical_size = 424
    arcsecs = historical_size * zoomed_pixscale

    native_pixscale = 0.262
    pixel_extent = np.ceil(arcsecs / native_pixscale).astype(int)

    # Two cases. Either galaxy is extended beyond maxsize, in which case download at maxsize and dif scale,
    # or (more often) it's small, and everything's okay
    params = {
        'ra': ra,
        'dec': dec,
        'layer': 'decals-dr{}'.format(data_release)
        # 'layer': 'sdss'.format(data_release)
    }

    if pixel_extent < max_size:
        params['size'] = pixel_extent
        query_params = 'ra={}&dec={}&size={}&layer={}'.format(params['ra'], params['dec'], params['size'], params['layer'])
    else:
        # forced to rescale to keep galaxy to reasonable number of pixels
        pixel_scale = arcsecs / max_size
        params['size'] = max_size
        params['pixscale'] = pixel_scale
        query_params = 'ra={}&dec={}&size={}&layer={}&pixscale={}'.format(params['ra'], params['dec'], params['size'], params['layer'], params['pixscale'])

    if img_format == 'jpg':
        img_format = 'jpeg'

    if data_release == '1':
        url = "http://imagine.legacysurvey.org/{}-cutout?{}".format(img_format, query_params)
    elif data_release == '2' or '3' or '5':
        url = "http://legacysurvey.org/viewer/{}-cutout?{}".format(img_format, query_params)
    else:
        raise ValueError('Data release "{}" not recognised'.format(data_release))

    return url


def make_png_from_fits(fits_loc, png_loc, png_size):
    '''
    Create png from multi-band fits

    Args:
        fits_loc (str): location of .fits to create png from
        png_loc (str): location to save png

    Returns:
        None
    '''

    # Set parameters for RGB image creation
    _scales = dict(
        g=(2, 0.008),
        r=(1, 0.014),
        z=(0, 0.019))
    _mnmx = (-0.5, 300)

    try:
        img, hdr = fits.getdata(fits_loc, 0, header=True)
    except Exception:
        warnings.warn('Invalid fits at {}'.format(fits_loc))
    else:  # if no exception getting image
        rgbimg = dr2_style_rgb(
            (img[0, :, :], img[1, :, :], img[2, :, :]),
            'grz',
            mnmx=_mnmx,
            arcsinh=1.,
            scales=_scales,
            desaturate=True)
        save_carefully_resized_png(png_loc, rgbimg, target_size=png_size)


def save_carefully_resized_png(png_loc, native_image, target_size):
    """
    # TODO
    Args:
        png_loc ():
        native_image ():
        target_size ():

    Returns:

    """
    native_pil_image = Image.fromarray(np.uint8(native_image * 255.), mode='RGB')
    nearest_image = native_pil_image.resize(size=(target_size, target_size), resample=Image.LANCZOS)
    nearest_image = nearest_image.transpose(Image.FLIP_TOP_BOTTOM)  # to align with north/east
    nearest_image.save(png_loc)


def check_images_are_downloaded(catalog, n_processes=10):
    """
    Record if images are downloaded. Add 'fits_ready', 'png_ready' and 'fits_complete' columns to catalog.

    Args:
        catalog (astropy.Table): joint NSA/decals catalog
        n_processes (int): number of processes to check images with (in parallel)

    Returns:
        (astropy.Table) catalog with image quality check columns added
    """
    manual_chunksize = 20000
    remaining_catalog = catalog.copy()
    results = []
    while True:
        print('Images left: {}'.format(len(remaining_catalog)))
        chunk = remaining_catalog[:manual_chunksize]
        remaining_catalog = remaining_catalog[manual_chunksize:]
        pool = multiprocessing.Pool(n_processes)
        result = list(tqdm(
            pool.imap(check_image_is_downloaded, chunk),
            total=len(catalog),
            unit='checked'))
        results.append(result)
        pool.close()
        pool.join()
        if len(remaining_catalog) == 0:
            break

    result = [quality_check_lst for lst in results for quality_check_lst in lst]
    catalog['fits_ready'] = [result[n][0] for n in range(len(catalog))]
    catalog['fits_filled'] = [result[n][1] for n in range(len(catalog))]
    catalog['png_ready'] = [result[n][2] for n in range(len(catalog))]

    return catalog


def check_image_is_downloaded(galaxy):
    downloaded, complete = get_download_quality_of_fits(galaxy['fits_loc'])
    if downloaded:  # fits must be ready for png to be ready
        png_ready = os.path.exists(galaxy['png_loc'])
    else:
        png_ready = False
    return downloaded, complete, png_ready


def get_download_quality_of_fits(fits_loc, badmax_limit=0.2):
    """
    Find if fits at fits_loc a) opens b) has few bad pixels

    Args:
        fits_loc (str): location of fits file to open
        badmax_limit(float): maximum ratio of empty pixels for image to be considered 'correct'

    Returns:
        (bool) is image downloaded?
        (bool) is empty pixel ratio below the allowed limit?
    """

    try:
        img = fits.getdata(fits_loc)
        complete = few_missing_pixels(img, badmax_limit)
        return True, complete
    except:  # image fails to open for any reason (not existing, corrupt, etc)
        return False, False


@jit  # just-in-time compile to C for speed (not actually much faster)
def few_missing_pixels(img, badmax_limit):
    """
    Find if img contains few NaN pixels e.g. from incomplete imaging

    Args:
        img (np.array): multi-band (i.e. 3-dim) pixel data to check
        badmax_limit(float): maximum ratio of empty pixels for image to be considered 'correct' e.g. 0.2 (20%)

    Returns:
        (bool) True if few NaN pixels, else False

    """
    badmax = 0.
    for j in range(img.shape[0]):
        band = img[j, :, :]
        nbad = (band == 0.).sum() + np.isnan(band).sum()  # count of bad pixels in band
        fracbad = nbad / np.prod(band.shape)  # fraction of bad pixels in band
        badmax = max(badmax, fracbad)  # update worst band fraction

    # if worst fraction of bad pixels is < badmax_limit, consider image as 'good'
    if badmax < badmax_limit:
        return True
    else:
        return False
