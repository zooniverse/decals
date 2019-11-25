# imgray2fits CL0024.png -over -header det.fits
# Converts a grayscale image to a FITS file

# im2rgbfits CL0024.png -over -header det.fits
# WILL HONOR WCS FROM headerfile

# im2rgbfits.py
# ~/ACS/CL0024/color/production/color.py
# ALSO SEE pyfits.pdf (Pyfits manual)

#from coetools import *
import sys
from glob import glob
from os.path import exists

import pyfits
from PIL import Image
from numpy import *


#################################

def str2num(str, rf=0):
    """CONVERTS A STRING TO A NUMBER (INT OR FLOAT) IF POSSIBLE
    ALSO RETURNS FORMAT IF rf=1"""
    try:
        num = string.atoi(str)
        format = 'd'
    except:
        try:
            num = str.atof()
            format = 'f'
        except:
            if not str.strip():
                num = None
                format = ''
            else:
                words = str.split()
                if len(words) > 1:
                    num = map(str2num, tuple(words))
                    format = 'l'
                else:
                    num = str
                    format = 's'
    if rf:
        return (num, format)
    else:
        return num

def loadgray(infile):
    """Load grayscale image"""
    im = Image.open(infile)
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    data = asarray(im)  # numpy
    data.flags.writeable = True  # DEFAULT IS CAN'T EDIT IT!
    return data


def params_cl(converttonumbers=True):
    """RETURNS PARAMETERS FROM COMMAND LINE ('cl') AS DICTIONARY:
    KEYS ARE OPTIONS BEGINNING WITH '-'
    VALUES ARE WHATEVER FOLLOWS KEYS: EITHER NOTHING (''), A VALUE, OR A LIST OF VALUES
    ALL VALUES ARE CONVERTED TO INT / FLOAT WHEN APPROPRIATE"""
    list = sys.argv[:]
    i = 0
    dict = {}
    oldkey = ""
    key = ""
    list.append('')  # EXTRA ELEMENT SO WE COME BACK AND ASSIGN THE LAST VALUE
    while i < len(list):
        if striskey(list[i]) or not list[i]:  # (or LAST VALUE)
            if key:  # ASSIGN VALUES TO OLD KEY
                if value:
                    if len(value) == 1:  # LIST OF 1 ELEMENT
                        value = value[0]  # JUST ELEMENT
                dict[key] = value
            if list[i]:
                key = list[i][1:] # REMOVE LEADING '-'
                value = None
                dict[key] = value  # IN CASE THERE IS NO VALUE!
        else: # VALUE (OR HAVEN'T GOTTEN TO KEYS)
            if key: # (HAVE GOTTEN TO KEYS)
                if value:
                    if converttonumbers:
                        value.append(str2num(list[i]))
                    else:
                        value = value + ' ' + list[i]
                else:
                    if converttonumbers:
                        value = [str2num(list[i])]
                    else:
                        value = list[i]
        i += 1

    return dict

def striskey(str):
    """IS str AN OPTION LIKE -C or -ker
    (IT'S NOT IF IT'S -2 or -.9)"""
    iskey = 0
    if str:
        if str[0] == '-':
            iskey = 1
            if len(str) > 1:
                iskey = str[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    return iskey

def decapfile(name, ext=''):
    """REMOVE EXTENSION FROM FILENAME IF PRESENT
    IF ext LEFT BLANK, THEN ANY EXTENSION WILL BE REMOVED"""
    if ext:
        if ext[0] <> '.':
            ext = '.' + ext
        n = len(ext)
        if name[-n:] == ext:
            name = name[:-n]
    else:
        if strend(name, '.gz'):
            name = name[-3:]
        i = name.rfind('.')
        if i > -1:
            name = name[:i]
    return name

def strend(str, phr):
    return str[-len(phr):] == phr


#################################

def imgray2fits(infile, fitsfile='', overwrite=False, headerfile=None, flip=False):
    if fitsfile == '':
        fitsfile = decapfile(infile) + '.fits'

    if exists(fitsfile):
        if overwrite:
            delfile(fitsfile)
        else:
            print fitsfile, 'EXISTS'
            sys.exit(1)
    
    data = loadgray(infile)  # coeim.py
    
    #hdu = pyfits.PrimaryHDU()
    header = headerfile and pyfits.getheader(headerfile)
    hdu = pyfits.PrimaryHDU(None, header)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(fitsfile)

    try:  # If there's a 'SCI' extension, then that's where the WCS is
        header = pyfits.getheader(headerfile, 'SCI')
    except:
        pass
    
    if header <> None:
        if 'EXTNAME' in header.keys():
            del(header['EXTNAME'])
    
    if flip:
        data = flipud(data)
    
    pyfits.append(fitsfile, data, header)
    
    print fitsfile, 'PRODUCED'
    #print fitsfile, 'NOW READY FOR "Open RGB Fits Image" in ds9'


if __name__ == '__main__':
    infile = sys.argv[1]
    
    outfile = ''
    if len(sys.argv) > 2:
        file2 = sys.argv[2]
        if file2[0] <> '-':
            outfile = file2
    
    params = params_cl()
    overwrite = 'over' in params.keys()
    headerfile = params.get('header', None)
    
    if ('*' in infile) or ('?' in infile):
        infiles = glob(infile)
        outfile = ''
    else:
        infiles = [infile]

    for infile in infiles:
        imgray2fits(infile, outfile, overwrite=overwrite, headerfile=headerfile)


#hdulist = pyfits.open(fitsfile)
#hdulist.info()
