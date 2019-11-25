# Another method to create RGB images. Possibly used in DR1, def. not in DR2

import numpy as np

#+
#NAME:
#  arcsinh_fit
#PURPOSE:
#  scales the FITS image by a specified degree of nonlinearity
#INPUTS:
#  colors      - (3xNXxNY) numpy array that contains the R/G/B images
#OPTIONAL INPUTS:
#  nonlinearity- 'b'
#              - b=0 for linear fit
#              - default is 3
#KEYWORDS:
#
#OUTPUTS:
#  Scaled FITS image
#BUGS:
#  
#REVISION HISTORY:
#  2 Jul 2014 - ported from Nick Wherry's IDL routine NW_ARCSINH_FIT - K. Willett
#-

def arcsinh_fit(colors,nonlinearity=3.):
    
    color_arr = np.array(colors)

    if nonlinearity != 0:
        radius = color_arr.sum(axis=0)
        radius[radius == 0] += 1

        val = np.arcsinh(radius*nonlinearity)/nonlinearity
        fitted_colors = color_arr * val / radius
    else:
        fitted_colors = color_arr

    return fitted_colors

#+
#NAME:
#  fit_to_box
#PURPOSE:
#  Limits the pixel values of the image to a 'box', so that the colors
#  do not saturate to white but to a specific color.
#INPUTS:
#  colors      - (NXxNYx3) array that contains the R/G/B images
#OPTIONAL INPUTS:
#  origin      - (3x1) array containing R0/G0/B0
#              - default is [0,0,0]
#KEYWORDS:
#
#OUTPUTS:
#  The color limited image
#BUGS:
#  
#REVISION HISTORY:
#  2 Jul 2014 - ported from Nick Wherry's IDL routine NW_FIT_TO_BOX - K. Willett
#-
def fit_to_box(colors,origin=[0,0,0]):

    color_arr = np.array(colors)
    
    # Creates an 'origin' array
    origin_arr = np.zeros_like(color_arr)
    for idx,o in enumerate(origin):
       origin_arr[idx,:,:] = o

    pos_dist = 1 - origin_arr
    
    factor = (color_arr / pos_dist).max(axis=0)
    factor[factor < 1.0] = 1.0

    boxed_colors = colors / factor

    return boxed_colors


#+
#NAME:
#  float_to_byte
#PURPOSE:
#  Converts floats of an array to bytes
#INPUTS:
#  image       - image array
#OPTIONAL INPUTS:
#  none
#KEYWORDS:
#  none
#OUTPUTS:
#  The float-value image
#REVISION HISTORY:
#  2 Jul 2014 - ported from Nick Wherry's IDL routine NW_FLOAT_TO_BYTE - K. Willett
#-
def float_to_byte(image):
    byte_image = bytearray(image)
    return byte_image


#+
#NAME:
#  scale_rgb
#PURPOSE:
#  mulitiplies the RGB image by their respective scales
#CALLING SEQUENCE:
#  nw_scale_rgb, colors, [scales=]
#INPUTS:
#  colors      - (3xNXxNY) array containing the R, G, and B
#OPTIONAL INPUTS:
#  scales      - list of len(3) to scale the R/G/B
#              - defaults are [4.9,5.7,7.8]
#KEYWORDS:
#  none
#OUTPUTS:
#  The RGB image 
#BUGS:
#  
#DEPENDENCIES:
#
#REVISION HISTORY:
#  2 Jul 2014 - ported from Nick Wherry's IDL routine NW_SCALE_RGB - K. Willett
#-
def scale_rgb(colors,scales=[4.9,5.7,7.8]):

    scaled_colors = np.zeros_like(colors)
    for idx,s in enumerate(scales):
        scaled_colors[idx,:,:] = colors[idx,:,:] * s
    
    return scaled_colors
