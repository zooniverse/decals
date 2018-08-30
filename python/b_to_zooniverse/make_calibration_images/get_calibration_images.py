import os
import functools
from multiprocessing.dummy import Pool as ThreadPool

from astropy.io import fits
from tqdm import tqdm

from a_download_decals.get_images.download_images_threaded import get_loc, save_carefully_resized_png


def make_catalog_png_images(catalog, img_creator_func, png_dir, size=424, n_processes=10, overwrite=False):
    """
    Create calibration images in two styles: as with DR2 (by Kyle Willet) and with stronger colours (new)
    The impact on classification performance will be tested
    Ignores 'png_loc' column of catalog in favour of png_loc generated from png_dir argument
    Args:
        catalog (astropy.Table): catalog of galaxies to save png of. 'png_loc' column will be ignored.
        img_creator_func (function): function to map nanomaggie fits array (c, h, w) to png array (h, w, c)
        png_dir (str): root directory to save new pngs. Subdirectories will be created
        size (int): dimensions to save png images
        n_processes (int): number of parallel processes to save calibration images with
        overwrite (bool): if True, create new calibration images. Else, this function does nothing.

    Returns:
        (astropy.Table) calibration_catalog with png_loc column added
    """
    catalog = catalog.copy()  # avoid mutating original catalog

    if not os.path.isdir(png_dir):
        os.mkdir(png_dir)
    assert os.path.isdir(png_dir)
    catalog['png_loc'] = [get_loc(png_dir, galaxy, 'png') for galaxy in catalog]

    pbar = tqdm(total=len(catalog), unit=' png created')

    kwargs = {
        'size': size,
        'img_creator_func': img_creator_func,
        'overwrite': overwrite,
        'pbar': pbar
    }
    save_calibration_images_of_galaxy_partial = functools.partial(save_image_of_galaxy, **kwargs)

    pool = ThreadPool(n_processes)
    pool.map(save_calibration_images_of_galaxy_partial, catalog)
    pbar.close()
    pool.close()
    pool.join()

    return catalog


def save_image_of_galaxy(galaxy, size, img_creator_func, overwrite=False, pbar=None):
    """

    Args:
        galaxy (dict): galaxy to save png of
        size (int): size of output png e.g. 424
        img_creator_func (function): function to map nanomaggie fits array (c, h, w) to png array (h, w, c)
        overwrite (bool): if True, overwrite existing png. Else, skip existing png.
        pbar (tqdm.pbar): tqdm progress bar

    Returns:
        None
    """

    if overwrite or not os.path.exists(galaxy['png_loc']):
        try:
            assert os.path.exists(galaxy['fits_loc'])
            img_data = fits.getdata(galaxy['fits_loc'])
        except:
            print('Fatal error: no or invalid fits at ' + galaxy['fits_loc'], flush=True)
            exit(1)
            if pbar:
                pbar.update()
            return None

        img = img_creator_func(img_data)

        save_carefully_resized_png(galaxy['png_loc'], img, target_size=size)

    if pbar:
        pbar.update()
