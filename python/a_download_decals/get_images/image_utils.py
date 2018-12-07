import numpy as np
# expects [channel, x, y] shape images, in fits style
# unlike ML style of [n, x, y, channel]


def dr2_style_rgb(imgs, bands, mnmx=None, arcsinh=None, scales=None, desaturate=False):
    '''
    Given a list of image arrays in the given bands, returns a scaled RGB image.
    Originally written by Dustin Lang and used by Kyle Willett for DECALS DR1/DR2 Galaxy Zoo subjects

    Args:
        imgs (list): numpy arrays, all the same size, in nanomaggies
        bands (list): strings, eg, ['g','r','z']
        mnmx (min,max), values that will become black/white *after* scaling. Default is (-3,10)):
        arcsinh (bool): if True, use nonlinear scaling (as in SDSS)
        scales (str): Override preset band scaling. Dict of form {band: (plane index, scale divider)}
        desaturate (bool): If [default=False] desaturate pixels dominated by a single colour

    Returns:
        (np.array) of shape (H, W, 3) with values between 0 and 1 of pixel values for colour image
    '''

    bands = ''.join(bands)  # stick list of bands into single string

    # first number is index of that band
    # second number is scale divisor - divide pixel values by scale divisor for rgb pixel value
    grzscales = dict(
        g=(2, 0.0066),
        r=(1, 0.01385),
        z=(0, 0.025),
    )

    if scales is None:
        if bands == 'grz':
            scales = grzscales
        elif bands == 'urz':
            scales = dict(
                u=(2, 0.0066),
                r=(1, 0.01),
                z=(0, 0.025),
            )
        elif bands == 'gri':
            scales = dict(
                g=(2, 0.002),
                r=(1, 0.004),
                i=(0, 0.005),
            )
        else:
            scales = grzscales

    #  create blank matrix to work with
    h, w = imgs[0].shape
    rgb = np.zeros((h, w, 3), np.float32)

    # Copy each band matrix into the rgb image, dividing by band scale divisor to increase pixel values
    for im, band in zip(imgs, bands):
        plane, scale = scales[band]
        rgb[:, :, plane] = (im / scale).astype(np.float32)

    # TODO mnmx -> (min, max)
    # cut-off values for non-linear arcsinh map
    if mnmx is None:
        mn, mx = -3, 10
    else:
        mn, mx = mnmx

    if arcsinh is not None:
        # image rescaled by single-pixel not image-pixel, which means colours depend on brightness
        rgb = nonlinear_map(rgb, arcsinh=arcsinh)
        mn = nonlinear_map(mn, arcsinh=arcsinh)
        mx = nonlinear_map(mx, arcsinh=arcsinh)

    # lastly, rescale image to be between min and max
    rgb = (rgb - mn) / (mx - mn)

    # default False, but downloader sets True
    if desaturate:
        # optionally desaturate pixels that are dominated by a single
        # colour to avoid colourful speckled sky

        # reshape rgb from (h, w, 3) to (3, h, w)
        RGBim = np.array([rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]])
        a = RGBim.mean(axis=0)  # a is mean pixel value across all bands, (h, w) shape
        # putmask: given array and mask, set all mask=True values of array to new value
        np.putmask(a, a == 0.0, 1.0)  # set pixels with 0 mean value to mean of 1. Inplace?
        acube = np.resize(a, (3, h, w))  # copy mean value array (h,w) into 3 bands (3, h, w)
        bcube = (RGBim / acube) / 2.5  # bcube: divide image by mean-across-bands pixel value, and again by 2.5 (why?)
        mask = np.array(bcube)  # isn't bcube already an array?
        wt = np.max(mask, axis=0)  # maximum per pixel across bands of mean-band-normalised rescaled image
        # i.e largest relative deviation from mean
        np.putmask(wt, wt > 1.0, 1.0)  # clip largest allowed relative deviation to one (inplace?)
        wt = 1 - wt  # invert relative deviations
        wt = np.sin(wt*np.pi/2.0)  # non-linear rescaling of relative deviations
        temp = RGBim * wt + a*(1-wt) + a*(1-wt)**2 * RGBim  # multiply by weights in complicated fashion
        rgb = np.zeros((h, w, 3), np.float32)  # reset rgb to be blank
        for idx, im in enumerate((temp[0, :, :], temp[1, :, :], temp[2, :, :])):  # fill rgb with weight-rescaled rgb
            rgb[:, :, idx] = im

    clipped = np.clip(rgb, 0., 1.)  # set max/min to 0 and 1

    return clipped


def decals_internal_rgb(imgs, bands, mnmx=None, arcsinh=None, scales=None,
                        clip=True):
    """
    Given a list of images in the given bands, returns a scaled RGB-like matrix.
    Written by Dustin Lang and used internally by DECALS collaboration
    Copied from https://github.com/legacysurvey/legacypipe/tree/master/py/legacypipe repo
    Not recommended - tends to oversaturate galaxy center

    Args:
        imgs (list): numpy arrays, all the same size, in nanomaggies
        bands (list): strings, eg, ['g','r','z']
        mnmx (min,max), values that will become black/white *after* scaling. ):
        arcsinh (bool): if True, use nonlinear scaling (as in SDSS)
        scales (str): Override preset band scaling. Dict of form {band: (plane index, scale divider)}
        clip (bool): if True, restrict output values to range (0., 1.)

    Returns:
        (np.array) of shape (H, W, 3) of pixel values for colour image

    """

    bands = ''.join(bands)

    grzscales = dict(g=(2, 0.0066),
                     r=(1, 0.01),
                     z=(0, 0.025),
                     )

    if scales is None:
        if bands == 'grz':
            scales = grzscales
        elif bands == 'urz':
            scales = dict(u=(2, 0.0066),
                          r=(1, 0.01),
                          z=(0, 0.025),
                          )
        elif bands == 'gri':
            scales = dict(g=(2, 0.002),
                          r=(1, 0.004),
                          i=(0, 0.005),
                          )
        elif bands == 'ugriz':
            scales = dict(g=(2, 0.0066),
                          r=(1, 0.01),
                          i=(0, 0.05),
                          )
        else:
            scales = grzscales

    h, w = imgs[0].shape
    rgb = np.zeros((h, w, 3), np.float32)
    for im, band in zip(imgs, bands):
        if not band in scales:
            print('Warning: band', band, 'not used in creating RGB image')
            continue
        plane, scale = scales.get(band, (0, 1.))
        rgb[:, :, plane] = (im / scale).astype(np.float32)

    if mnmx is None:
        mn, mx = -3, 10
    else:
        mn, mx = mnmx

    if arcsinh is not None:
        def nlmap(x):
            return np.arcsinh(x * arcsinh) / np.sqrt(arcsinh)

        rgb = nlmap(rgb)
        mn = nlmap(mn)
        mx = nlmap(mx)

    rgb = (rgb - mn) / (mx - mn)

    if clip:
        return np.clip(rgb, 0., 1.)
    return rgb


def lupton_rgb(imgs, bands='grz', arcsinh=1., mn=0.1, mx=100., desaturate=False, desaturate_factor=.01):
    """
    Create human-interpretable rgb image from multi-band pixel data
    Follow the comments of Lupton (2004) to preserve colour during rescaling
    1) linearly scale each band to have good colour spread (subjective choice)
    2) nonlinear rescale of total intensity using arcsinh
    3) linearly scale all pixel values to lie between mn and mx
    4) clip all pixel values to lie between 0 and 1

    Optionally, desaturate pixels with low signal/noise value to avoid speckled sky (partially implemented)

    Args:
        imgs (list): of 2-dim np.arrays, each with pixel data on a band # TODO refactor to one 3-dim array
        bands (str): ordered characters of bands of the 2-dim pixel arrays in imgs
        arcsinh (float): softening factor for arcsinh rescaling
        mn (float): min pixel value to set before (0, 1) clipping
        mx (float): max pixel value to set before (0, 1) clipping
        desaturate (bool): If True, reduce saturation on low S/N pixels to avoid speckled sky
        desaturate_factor (float): parameter controlling desaturation. Proportional to saturation.

    Returns:
        (np.array) of shape (H, W, 3) of pixel values for colour image
    """

    size = imgs[0].shape[1]
    grzscales = dict(g=(2, 0.00526),
                     r=(1, 0.008),
                     z=(0, 0.0135)
                     )

    # set the relative intensities of each band to be approximately equal
    img = np.zeros((size, size, 3), np.float32)
    for im, band in zip(imgs, bands):
        plane, scale = grzscales.get(band, (0, 1.))
        img[:, :, plane] = (im / scale).astype(np.float32)

    I = img.mean(axis=2, keepdims=True)

    if desaturate:
        img_nanomaggies = np.zeros((size, size, 3), np.float32)
        for im, band in zip(imgs, bands):
            plane, scale = grzscales.get(band, (0, 1.))
            img_nanomaggies[:, :, plane] = im.astype(np.float32)
        img_nanomaggies_nonzero = np.clip(img_nanomaggies, 1e-9, None)
        img_ab_mag = 22.5 - 2.5 * np.log10(img_nanomaggies_nonzero)
        img_flux = np.power(10, img_ab_mag / -2.5) * 3631
        # DR1 release paper quotes 90s exposure time per band, 900s on completion
        # TODO assume 3 exposures per band per image. exptime is per ccd, nexp per tile, will be awful to add
        exposure_time_seconds = 90. * 3.
        photon_energy = 600. * 1e-9  # TODO assume 600nm mean freq. for gri bands, can improve this
        img_photons = img_flux * exposure_time_seconds / photon_energy
        img_photons_per_pixel = np.sum(img_photons, axis=2, keepdims=True)

        mean_all_bands = img.mean(axis=2, keepdims=True)
        deviation_from_mean = img - mean_all_bands
        signal_to_noise = np.sqrt(img_photons_per_pixel)
        saturation_factor = signal_to_noise * desaturate_factor
        # if that would imply INCREASING the deviation, do nothing
        saturation_factor[saturation_factor > 1] = 1.
        img = mean_all_bands + (deviation_from_mean * saturation_factor)

    rescaling = nonlinear_map(I, arcsinh=arcsinh)/I
    rescaled_img = img * rescaling

    rescaled_img = (rescaled_img - mn) * (mx - mn)
    rescaled_img = (rescaled_img - mn) * (mx - mn)

    return np.clip(rescaled_img, 0., 1.)


def nonlinear_map(x, arcsinh=1.):
    """
    Apply non-linear map to input matrix. Useful to rescale telescope pixels for viewing.
    Args:
        x (np.array): array to have map applied
        arcsinh (np.float):

    Returns:
        (np.array) array with map applied
    """
    return np.arcsinh(x * arcsinh)


def get_dr2_style_image(img_data):
    """
    Create png-scaled array in style of DECALS DR2
    Wraps the required 'magic numbers'
    Args:
        img_data (np.array): flux in nanomaggies in shape (3, height, width) (fits shape convention)

    Returns:
         (np.array) of shape (height, width, 3) of pixel values for colour image
    """
    img_bands = (img_data[0, :, :], img_data[1, :, :], img_data[2, :, :])
    kwargs = {
        'scales': dict(
            g=(2, 0.008),
            r=(1, 0.014),
            z=(0, 0.019)),
        'bands': 'grz',
        'mnmx': (-0.5, 300),
        'arcsinh': 1.,
        'desaturate': False
}
    return dr2_style_rgb(img_bands, **kwargs)


def get_colour_style_image(img_data):
    """
    Create png-scaled array in style of Lupton
    Wraps the required 'magic numbers'
    Args:
        img_data (np.array): flux in nanomaggies in shape (3, height, width) (fits shape convention)

    Returns:
         (np.array) of shape (height, width, 3) of pixel values for colour image
    """
    img_bands = (img_data[0, :, :], img_data[1, :, :], img_data[2, :, :])
    kwargs = {
        'arcsinh': .3,
        'mn': 0,
        'mx': .4
    }
    return lupton_rgb(img_bands, **kwargs)
