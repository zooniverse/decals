from astropy.io import fits
import numpy as np
from PIL import Image

from get_images.image_utils import dr2_style_rgb, lupton_rgb
import png


def save_aliasing_sample():
    """
    Experiment with
    - resizing images to reduce aliasing
    - saving higher bit depth images
    - png vs jpg
    Returns:
        None
    """
    # J000150.59
    # ra = 0.45966873923457313
    # dec = 1.0320259289150582
    # pixscale = 0.1
    # file_loc = '/Volumeas/external/decals/fits/dr5/J000/J000150.59+010157.1.fits'
    file_loc = '/Volumes/external/decals/fits/dr5/J000/J000001.85+004309.3.fits'

    # J000001.85
    # ra = 0.007753869567118207
    # dec = 0.7192492767595782
    # pixscale = 0.1
    cutout_loc = '/Data/repos/decals/python/test_examples/sample/cutout_147.4958_1.0684.fits'

    files = [file_loc, cutout_loc]

    for file_loc in files:
        save_with_aliasing_options(file_loc)


def save_with_aliasing_options(file_loc):

    sample_dir = 'python/test_examples/sample'
    iauname = file_loc.split(sep='/')[-1][:-5]

    img_data = fits.getdata(file_loc, 1)
    print(img_data.shape)

    stacked_data = np.sum(img_data, axis=0)
    save_loc = '{}/{}.fits'.format(sample_dir, iauname)
    fits.writeto(save_loc, stacked_data, overwrite=True)

    img_bands = (img_data[0, :, :], img_data[1, :, :], img_data[2, :, :])

    dr2_img = get_dr2_style(img_bands)
    lupton_img = get_lupton(img_bands)
    write_16bit_png_pypng(lupton_img, sample_dir, iauname + '_16bit_pypng')
    write_16bit_png_mpl(lupton_img, sample_dir, iauname + '_16bit_mpl')
    # save_png_and_jpg(dr2_img, sample_dir, iauname + '_raw_dr2')
    # save_png_and_jpg(lupton_img, sample_dir, iauname + '_raw_lupton')

    # downsampling_factor = 4
    # dr2_dec = decimate(dr2_img, downsampling_factor)
    # lupton_dec = decimate(dr2_img, downsampling_factor)
    # save_png_and_jpg(dr2_dec, sample_dir, iauname + '_dec_dr2')
    # save_png_and_jpg(lupton_dec, sample_dir, iauname + '_dec_lupton')

    # save_aliased_png_and_jpg(dr2_img, sample_dir, iauname + '_aliased_dr2')
    # save_aliased_png_and_jpg(lupton_img, sample_dir, iauname + '_aliased_lupton')


def get_dr2_style(img_bands):
    _scales = dict(
        g=(2, 0.008),
        r=(1, 0.014),
        z=(0, 0.019))
    _mnmx = (-0.5, 300)

    return dr2_style_rgb(
            img_bands,
            'grz',
            mnmx=_mnmx,
            arcsinh=1.,
            scales=_scales,
            desaturate=True)


def get_lupton(img_bands, size=424):
    kwargs = {
        'arcsinh': .3,
        'mn': 0,
        'mx': .4,
        'size': size
    }
    return lupton_rgb(img_bands, **kwargs)


def save_png_and_jpg(image, dir, name):
    png_save_loc = '{}/{}.png'.format(dir, name)
    pil_image = Image.fromarray(np.uint8(image * 255.), mode='RGB')
    pil_image.save(png_save_loc, compress_level=0)
    jpg_save_loc = '{}/{}.jpg'.format(dir, name)
    pil_image.save(jpg_save_loc)
    tiff_save_loc = '{}/{}.tiff'.format(dir, name)
    tiff_image = Image.fromarray(np.uint16(image), mode='F')
    tiff_image.save(tiff_save_loc)


def save_aliased_png_and_jpg(image, dir, name):
    original_dim = image.shape[1]  # assumes square
    print(original_dim)
    png_save_loc = '{}/{}.png'.format(dir, name)
    pil_image = Image.fromarray(np.uint16(image * 255.))
    oversampled = pil_image.resize(size=(original_dim * 5, original_dim * 5))
    resampled = oversampled.resize(size=(original_dim, original_dim))
    resampled.save(png_save_loc)
    jpg_save_loc = '{}/{}.jpg'.format(dir, name)
    resampled.save(jpg_save_loc)


def write_16bit_png_pypng(float_image, dir, name):
    image = np.uint16(float_image * 65535.)
    # Use pypng to write z as a color PNG.
    png_save_loc = '{}/{}.png'.format(dir, name)
    with open(png_save_loc, 'wb') as f:
        writer = png.Writer(width=image.shape[1], height=image.shape[0], bitdepth=16)
        z2list = image.reshape(-1, image.shape[1] * image.shape[2]).tolist()
        writer.write(f, z2list)
    """
    Normal RGB images (including default PNG) can only represent colour with 8-bit ints (aka bit depth)
    https://photography.tutsplus.com/articles/bit-depth-explained-in-depth--photo-8514
    That's why the int values are limited to 255
    this gives 255 ^ 3 possible colours per pixel
    This can cause color banding for smooth patches of similar colour:
    https://photographylife.com/what-is-color-banding-and-how-to-fix-it
    PNG support higher bit depths of 16+, which removes banding by allowing for more colours
    (65535 ^ 3 possible colours)
    However, it's a hassle to read and write as PIL does not support high bit depth colour images
    After working out how to do it with the 'pypng' library, the final images look effectively identical
    So let's not make life complicated - a million colours turns out to be plenty
    """


def write_16bit_png_mpl(float_image, dir, name):
    from skimage import io, exposure, img_as_uint, img_as_float
    # Use pypng to write z as a color PNG.
    png_save_loc = '{}/{}.png'.format(dir, name)
    with open(png_save_loc, 'wb') as f:
        io.use_plugin('freeimage')
        im = exposure.rescale_intensity(float_image, out_range='float')
        im = img_as_uint(im)
        io.imsave(png_save_loc, im)


if __name__ == '__main__':
    save_aliasing_sample()
