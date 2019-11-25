from __future__ import division

import os
import urllib
from multiprocessing import Value, Lock
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import progressbar as pb
from astropy.io import fits
from astropy.table import Table

widgets = ['Downloads: ', pb.Percentage(), ' ', pb.Bar(marker='0',left='[',right=']'), ' ', pb.ETA()]
cdx = 0
pbar = 0
class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()
    def change_value(self,v):
        with self.lock:
            self.val.value = v
    def increment(self):
        with self.lock:
            self.val.value += 1
    def value(self):
        with self.lock:
            return self.val.value

min_pixelscale = 0.10
def get_skyserver_jpeg(gal,jpegpath='../jpeg/nsa_not_gz'):
    timed_out = False
    # Download an RGB jpeg image from the SDSS skyserver

    # Get JPEG
    galname = gal['IAUNAME']
    jpeg_filename = "{0}/{1}.jpeg".format(jpegpath, galname)
    if os.path.exists(jpeg_filename) == False:
        params = urllib.urlencode({'ra':gal['RA'],'dec':gal['DEC'],'scale':max(min(gal['PETROTH50']*0.04,gal['PETROTH90']*0.02),min_pixelscale),'width':424,'height':424})
        url = "http://skyservice.pha.jhu.edu/DR12/ImgCutout/getjpeg.aspx?{0}".format(params)
        try:
            urllib.urlretrieve(url, jpeg_filename)
        except:
            timed_out = True
    cdx.increment()
    pbar.update(cdx.value())
    return timed_out

if __name__ == "__main__":
    nsa_version = '0_1_2'
    #nsa_not_gz = Table(fits.getdata('../fits/nsa_v{0}_not_in_GZ.fits'.format(nsa_version), 1))
    nsa_not_gz = Table(fits.getdata('../fits/nsa_v{0}_not_in_GZ_decals_bad_pix.fits'.format(nsa_version), 1))
    cdx=Counter(0)
    pbar = pb.ProgressBar(widgets=widgets, maxval=len(nsa_not_gz))
    pool=ThreadPool(8)
    pbar.start()
    results = pool.map(get_skyserver_jpeg, nsa_not_gz)
    pbar.finish()
    pool.close()
    pool.join()
    timed_out = np.array(results)

    logfile = "../failed_jpeg_downloads.log"
    flog = open(logfile,'w')
    print(flog, "\n".join(nsa_not_gz['IAUNAME'][timed_out]))
    flog.close()

    print("\n{0} total galaxies processed".format(len(nsa_not_gz)))
    print("{0} galaxies timed out downloading data from DR12 Skyserver".format(sum(timed_out)))
