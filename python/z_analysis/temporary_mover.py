import a_download_decals.download_decals_settings as settings
import subprocess
from multiprocessing.dummy import Pool as ThreadPool
import os

from tqdm import tqdm
from astropy.table import Table

from a_download_decals.get_images.download_images_threaded import get_loc

joint_catalog = Table.read(settings.joint_catalog_loc)


def get_old_fits_loc(fits_dir, galaxy):
    return '{}/{}.fits'.format(fits_dir, galaxy['iauname'])


def get_old_png_loc(png_dir, galaxy):
    return '{}/{}.png'.format(png_dir, galaxy['iauname'])

# new_root_fits_dir = '/data/galaxy_zoo/decals/fits/dr5'
# new_root_dir = 'Volumes/new_hdd/dr5'
# new_root_dir = '/data/galaxy_zoo/decals/png/dr5'
new_root_dir = '/Volumes/alpha/decals/fits/dr5'
current_root_dir = '/Volumes/EXTERNAL/decals/fits/dr5'


def move_galaxy(galaxy, current_root_dir=current_root_dir, new_root_dir=new_root_dir):
    # current_loc = get_old_fits_loc(current_root_fits_dir, galaxy)
    # target_loc = get_loc(new_root_fits_dir, galaxy, 'fits')
    # current_loc = get_old_png_loc(current_root_dir, galaxy)
    target_loc = get_loc(new_root_dir, galaxy, 'fits')
    current_loc = get_loc(current_root_dir, galaxy, 'fits')
    if os.path.exists(current_loc) and not os.path.exists(target_loc):
        command = 'mv {} {}'.format(current_loc, target_loc)
        result = subprocess.Popen(command, shell=True)
        name = result.pid
        try:
            result.wait(timeout=10)
        except Exception as err:
            print(err)
            print('timeout doing {}, {}'.format(command, name))

n_threads = 1
pool = ThreadPool(n_threads)
list(tqdm(pool.imap(move_galaxy, joint_catalog), total=len(joint_catalog), unit=' moved'))
pool.close()
pool.join()
