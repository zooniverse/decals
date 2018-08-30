import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from get_images.download_images_threaded import get_fits_loc

from a_download_decals.get_images import image_utils


def make_mosaic(catalog_sample, fits_to_rgb_instructions, output_loc):
    """
    Create tiled png image of galaxy catalog over many rgb options

    Args:
        catalog_sample (astropy.Table): galaxies to create images of
        fits_to_rgb_functions (list): dicts of {function, kwargs} for creating rgb images
        output_loc (str) save location for mosaic image


    Returns:
        None

    """
    num_rgb_functions = len(fits_to_rgb_instructions)
    num_galaxies = len(catalog_sample)

    fig, axes = plt.subplots(num_galaxies, num_rgb_functions, figsize=(len(fits_to_rgb_instructions) * 10, 200))
    for row_index, axes_row in enumerate(axes):
        img = fits.getdata(catalog_sample['fits_loc'][row_index])
        img_bands = (img[0, :, :], img[1, :, :], img[2, :, :])  # TODO rework image utils
        for col_index, ax in enumerate(axes_row):
            rgb_function = fits_to_rgb_instructions[col_index]['function']
            kwargs = fits_to_rgb_instructions[col_index]['kwargs']
            rgb = rgb_function(img_bands, **kwargs)
            ax.imshow(rgb, aspect='equal', extent=(0, 400, 0, 400))
            ax.set_xticks([])
            ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(output_loc)


if __name__ == '__main__':
    catalog_dir = '/data/galaxy_zoo/decals/catalogs'
    fits_dir = '/data/galaxy_zoo/decals/fits/dr5'
    catalog_sample = Table(fits.getdata('{}/nsa_v1_0_0_decals_dr5.fits'.format(catalog_dir))[:20])
    catalog_sample['fits_loc'] = [get_fits_loc(fits_dir, galaxy) for galaxy in catalog_sample]

    # print(catalog_sample.colnames)
    fits_to_rgb_instructions = [
        {
            'function': image_utils.dr2_style_rgb,
            'kwargs': {
                'scales': dict(
                    g=(2, 0.008),
                    r=(1, 0.014),
                    z=(0, 0.019)),
                'bands': 'grz',
                'mnmx': (-0.5, 300),
                'arcsinh': 1.,
                'desaturate': False
            }
        },
        {
            'function': image_utils.decals_internal_rgb,
            'kwargs':
                dict(mnmx=(-1, 100.),
                arcsinh=1.,
                bands='grz')
        },
        {
            'function': image_utils.lupton_rgb,
            'kwargs': {
                'arcsinh': .3,
                'mn': 0,
                'mx': .3
            }
        },
        {
            'function': image_utils.lupton_rgb,
            'kwargs': {
                'arcsinh': .3,
                'mn': 0,
                'mx': .4
            }
        },
        {
            'function': image_utils.lupton_rgb,
            'kwargs': {
                'arcsinh': .4,
                'mn': 0,
                'mx': .4
            }
        }
    ]

    make_mosaic(catalog_sample, fits_to_rgb_instructions, 'mosaic.png')