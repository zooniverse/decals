import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pytest
from astropy.io import fits


from a_download_decals.get_images import image_utils

TEST_EXAMPLES_DIR = 'python/test_examples'


@pytest.fixture()
def fits_loc():
    return '{}/example_a.fits'.format(TEST_EXAMPLES_DIR)


@pytest.fixture()
def jpeg_loc():
    return '{}/test_output.jpg'.format(TEST_EXAMPLES_DIR)


def image_data_by_band(fits_loc):
    img = fits.getdata(fits_loc)
    return (img[0, :, :], img[1, :, :], img[2, :, :])


@pytest.fixture()
def jpeg_creation_params():
    # Set parameters for RGB image creation
    return {
        'scales': dict(
            g=(2, 0.008),
            r=(1, 0.014),
            z=(0, 0.019)),
        'bands': 'grz',
        'mnmx': (-0.5, 300),
        'arcsinh': 1.,
        'desaturate': False
    }


@pytest.fixture()
def dustin_creation_params():
    return dict(
        mnmx=(-1, 100.),
        arcsinh=1.,
        bands='grz')


def plot_jpegs(jpegs, name):
    fig, axes = plt.subplots(1, 3)
    for ax_index, ax in enumerate(axes):
        cbar = ax.imshow(jpegs[ax_index])
    # fig.colorbar(cbar)
    plt.tight_layout()
    plt.savefig('{}/{}.jpg'.format(TEST_EXAMPLES_DIR, name))


def test_dstn_rgb_on_varying_brightness():
    original_data_by_band = image_data_by_band('{}/example_e.fits'.format(TEST_EXAMPLES_DIR))
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    desaturate_off = jpeg_creation_params()
    jpegs = [image_utils.dr2_style_rgb(image, **desaturate_off) for image in data]
    plot_jpegs(jpegs, 'ours_comparison')

    desaturate_on = desaturate_off
    desaturate_on['desaturate'] = True
    jpegs = [image_utils.dr2_style_rgb(image, **desaturate_on) for image in data]
    plot_jpegs(jpegs, 'ours_comparison_desaturate')


def test_decals_on_varying_brightness():
    original_data_by_band = image_data_by_band('{}/example_e.fits'.format(TEST_EXAMPLES_DIR))
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    jpegs = [image_utils.decals_internal_rgb(image, **dustin_creation_params()) for image in data]
    plot_jpegs(jpegs, 'dustin_comparison')


def test_lupton_on_varying_brightness():
    original_data_by_band = image_data_by_band('{}/example_e.fits'.format(TEST_EXAMPLES_DIR))
    data_up_20pc = [band * 2. for band in original_data_by_band]
    data_down_20pc = [band * 0.5 for band in original_data_by_band]

    data = [data_down_20pc, original_data_by_band, data_up_20pc]

    jpegs = [image_utils.lupton_rgb(image) for image in data]
    plot_jpegs(jpegs, 'lupton_comparison')


def test_lupton_on_varying_saturation():
    image_loc = '{}/example_e.fits'.format(TEST_EXAMPLES_DIR)
    # image_loc = '/data/temp/sandor_bars/decals/fits_native/dr5/J104/J104031.24+121739.8.fits'
    # image_loc = '/data/temp/sandor_bars/decals/fits_native/dr5/J133/J133729.36+040615.9.fits'
    # image_loc = '/Volumes/alpha/decals/fits_native/dr5/J000/J000001.03+003228.7.fits'

    original_data_by_band = image_data_by_band(image_loc)

    kwargs = {
        'arcsinh': .3,
        'mn': 0,
        'mx': .4
    }
    jpegs = [image_utils.lupton_rgb(original_data_by_band, **kwargs, desaturate=desaturate) for desaturate in [True, False]]
    plot_jpeg_pair(jpegs, 'lupton_comparison_desaturate')


def plot_jpeg_pair(jpegs, name):
    fig, axes = plt.subplots(ncols=2)
    for ax_index, ax in enumerate(axes):
        cbar = ax.imshow(jpegs[ax_index])
    plt.tight_layout()
    plt.savefig('{}/{}.jpg'.format(TEST_EXAMPLES_DIR, name))
