import a_download_decals.download_decals_settings as settings
import subprocess
from multiprocessing.dummy import Pool as ThreadPool
import os
import sys

import pandas as pd
from tqdm import tqdm
from astropy.table import Table
from pyspark import SparkContext, SparkConf

from a_download_decals.get_images.download_images_threaded import get_loc

joint_catalog = Table.read(settings.joint_catalog_loc)


# decals naming convention
# def get_old_fits_loc(fits_dir, galaxy):
#     return '{}/{}.fits'.format(fits_dir, galaxy['iauname'])
# def get_old_png_loc(png_dir, galaxy):
#     return '{}/{}.png'.format(png_dir, galaxy['iauname'])


# gz2 naming convention
# def get_old_fits_loc(fits_dir, galaxy):
#     return '{}/{}.fits'.format(fits_dir, galaxy['iauname'])
def get_old_png_loc(png_dir, galaxy):
    return '{}/{}.png'.format(png_dir, str(galaxy['dr7objid']))

def get_new_png_loc(png_dir, galaxy):
    target_dir = '{}/{}'.format(png_dir, str(galaxy['dr7objid'])[:6])
    if not os.path.isdir(target_dir):  # place each galaxy in a directory with first 3 letters of iauname (i.e. RA)
        try:
            os.mkdir(target_dir)
        except FileExistsError:  # when running multithreaded, another thread could make directory between checks
            if os.path.isdir(target_dir):
                pass
    return os.path.join(target_dir, '{}.png'.format(galaxy['dr7objid']))

# new_root_fits_dir = '/data/galaxy_zoo/decals/fits/dr5'
# new_root_dir = 'Volumes/new_hdd/dr5'
# new_root_dir = '/data/galaxy_zoo/decals/png/dr5'
new_root_dir = '/data/galaxy_zoo/gz2/png'
current_root_dir = '/Volumes/EXTERNAL/gz2/png'
assert os.path.exists(current_root_dir)
assert os.path.exists(new_root_dir)

def move_galaxy(data_str, current_root_dir=current_root_dir, new_root_dir=new_root_dir):
    data = data_str.split(',')
    assert len(data_str) != 1
    galaxy = {'dr7objid': data[0], 'png_loc': data[1]}
    # current_loc = get_old_fits_loc(current_root_fits_dir, galaxy)
    # target_loc = get_loc(new_root_fits_dir, galaxy, 'fits')
    # current_loc = get_old_png_loc(current_root_dir, galaxy)
    # target_loc = get_loc(new_root_dir, galaxy, 'fits')
    # current_loc = get_loc(current_root_dir, galaxy, 'fits')
    current_loc = get_old_png_loc(current_root_dir, galaxy)
    target_loc = get_new_png_loc(new_root_dir, galaxy)
    # return True  # temp
    if os.path.exists(current_loc) and not os.path.exists(target_loc):
        command = 'mv {} {}'.format(current_loc, target_loc)
        result = subprocess.Popen(command, shell=True)
        name = result.pid
        try:
            result.wait(timeout=10)
        except Exception as err:
            print(err)
            print('timeout doing {}, {}'.format(command, name))
    return 'completed'


if __name__ == '__main__':
    df = pd.read_csv(
        '/data/galaxy_zoo/gz2/subjects/all_labels_downloaded.csv', 
        usecols=['dr7objid', 'png_loc'],
        # nrows=100
        )
    print(df.iloc[0])
    print(len(df))

    df.to_csv('/data/galaxy_zoo/gz2/subjects/locations_only.csv', index=False, header=False)

    os.environ['PYSPARK_PYTHON'] = sys.executable  # path to current interpreter
    appName = 'hello_world'  # name to display
    master = 'local[3]'  # don't run on remote cluster. [*] indicates use all cores.
    # create launch configuration
    conf = SparkConf().setAppName(appName).setMaster(master) 
    sc = SparkContext(conf=conf)  # this tells spark how to access a cluster

    catalog = sc.textFile('/data/galaxy_zoo/gz2/subjects/locations_only.csv')
    results = catalog.map(move_galaxy)
    results.collect()

    # tqdm(df.apply(move_galaxy, axis=1), total=len(df), unit=' moved')

    # n_threads = 1
    # pool = ThreadPool(n_threads)
    # _, rows = df.iterrows()
    # list(tqdm(pool.imap(move_galaxy, rows), total=len(df), unit=' moved'))
    # pool.close()
    # pool.join()
