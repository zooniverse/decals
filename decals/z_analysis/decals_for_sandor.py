import for_sandor_settings as settings
from a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog, get_decals_bricks
from a_download_decals.get_decals_images_and_catalogs import get_decals
from shared_utilities import match_galaxies_to_catalog_table

from astropy.table import Table
import pandas as pd


def main():
    """
    Create the NSA-DECaLS-GZ catalog, download fits, produce png, and identify new subjects

    Returns:
        None
    """

    # specify execution options
    settings.new_catalog = True
    settings.new_images = True
    settings.overwrite_fits = False
    settings.overwrite_png = False
    settings.run_to = None
    #
    # usecols = [
    #     'ra',
    #     'dec',
    #     't05_bulge_prominence_a13_dominant_weighted_fraction',
    #     't08_odd_feature_a22_irregular_weighted_fraction',
    #     't05_bulge_prominence_a10_no_bulge_weighted_fraction',
    #     't04_spiral_a08_spiral_weighted_fraction',
    #     't02_edgeon_a05_no_weighted_fraction',
    #     't01_smooth_or_features_a02_features_or_disk_weighted_fraction'
    #     ]
    # gz2 = pd.read_csv('/data/galaxy_zoo/gz2/subjects/gz2_hart16.csv',
    #                   usecols=usecols)
    # gz2 = gz2[gz2['t02_edgeon_a05_no_weighted_fraction'] > 0.4]
    # gz2 = gz2[gz2['t01_smooth_or_features_a02_features_or_disk_weighted_fraction'] > 0.4]
    # gz2_no_bulge = gz2[gz2['t05_bulge_prominence_a10_no_bulge_weighted_fraction'] > 0.7][:100]
    # gz2_big_bulge = gz2[gz2['t05_bulge_prominence_a13_dominant_weighted_fraction'] > 0.7][:100]
    # gz2_no_bulge_spiral = gz2[(gz2['t05_bulge_prominence_a10_no_bulge_weighted_fraction'] > 0.7) & (gz2['t04_spiral_a08_spiral_weighted_fraction'] > 0.7)][:100]
    # gz2_big_bulge_spiral = gz2[(gz2['t05_bulge_prominence_a13_dominant_weighted_fraction'] > 0.7) & (gz2['t04_spiral_a08_spiral_weighted_fraction'] > 0.7)][:100]
    #
    # assert len(gz2_big_bulge_spiral > 0)
    #
    # gz2_no_bulge_table = Table.from_pandas(gz2_no_bulge)
    # gz2_big_bulge_table = Table.from_pandas(gz2_big_bulge)
    # gz2_no_bulge_spiral_table = Table.from_pandas(gz2_no_bulge_spiral)
    # gz2_big_bulge_spiral_table = Table.from_pandas(gz2_big_bulge_spiral)

    nsa = get_nsa_catalog(settings.nsa_catalog_loc, settings.nsa_version)
    print('nsa loaded')
    bricks = get_decals_bricks(settings.bricks_loc, settings.data_release)
    print('bricks loaded')

    # nsa_no_bulge, _ = match_galaxies_to_catalog_table(gz2_no_bulge_table, nsa)
    # nsa_big_bulge, _ = match_galaxies_to_catalog_table(gz2_big_bulge_table, nsa)
    # nsa_no_bulge_spiral, _ = match_galaxies_to_catalog_table(gz2_no_bulge_spiral_table, nsa)
    # nsa_big_bulge_spiral, _ = match_galaxies_to_catalog_table(gz2_big_bulge_spiral_table, nsa)

    # galaxies_to_include = {
    #     'J104031.24+121739.8',
    #     'J103846.59+054145.0',
    #     'J112147.02+040710.8',
    #     'J011341.82-000609.7',
    #     'J101819.60+070252.9',
    #     'J091135.57+325055.6',
    #     'J135406.26+052122.8',
    #     'J103351.36-003340.8',
    #     'J132132.19+121115.8',
    #     'J140808.50-014208.2',
    #     'J133729.36+040615.9',
    #     'J090339.90+032211.3',
    #     'J225246.39+010758.0',
    #     'J021219.80-004835.0',
    #     'J112736.73+002342.7'
    # }

    # print(nsa['iauname'] in galaxies_to_include)
    # nsa['selected'] = list(map(lambda x: x in galaxies_to_include, nsa['iauname']))
    # nsa_filtered = nsa[nsa['selected']]
    # print(len(nsa_filtered))

    nsa_filtered = nsa[:1000]

    # settings.fits_dir = '/data/temp/no_bulge/fits_native'.format(settings.data_release)
    # settings.png_dir = '/data/temp/no_bulge/png_native'.format(settings.data_release)
    # _ = get_decals(nsa_no_bulge, bricks, settings)
    #
    # settings.fits_dir = '/data/temp/big_bulge/fits_native'.format(settings.data_release)
    # settings.png_dir = '/data/temp/big_bulge/png_native'.format(settings.data_release)
    # _ = get_decals(nsa_big_bulge, bricks, settings)
    #
    # settings.fits_dir = '/data/temp/no_bulge_spiral/fits_native'.format(settings.data_release)
    # settings.png_dir = '/data/temp/no_bulge_spiral/png_native'.format(settings.data_release)
    # _ = get_decals(nsa_no_bulge_spiral, bricks, settings)
    #
    # settings.fits_dir = '/data/temp/big_bulge_spiral/fits_native'.format(settings.data_release)
    # settings.png_dir = '/data/temp/big_bulge_spiral/png_native'.format(settings.data_release)
    # _ = get_decals(nsa_big_bulge_spiral, bricks, settings)

    # settings.fits_dir = '/data/temp/comparison/decals/fits_native'.format(settings.data_release)
    # settings.png_dir = '/data/temp/comparison/decals/png_native'.format(settings.data_release)
    # _ = get_decals(nsa_filtered, bricks, settings)

    settings.fits_dir = '/data/temp/comparison/sdss/fits_native'.format(settings.data_release)
    settings.png_dir = '/data/temp/comparison/sdss/png_native'.format(settings.data_release)
    _ = get_decals(nsa_filtered, bricks, settings)


if __name__ == '__main__':
    main()
