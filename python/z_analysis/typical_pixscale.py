from astropy.table import Table
from astropy.io import fits
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

joint_catalog_loc = '/volumes/external/decals/catalogs/dr5_nsa1_0_0_to_upload.fits'
catalog = Table(fits.getdata(joint_catalog_loc))

min_pixelscale = 0.1
# catalog['pixscale'] = [max(min(galaxy['petroth50'] * 0.04, galaxy['petroth50'] * 0.02), min_pixelscale) for galaxy in catalog]
catalog['pixscale'] = [max(min(galaxy['petroth50'] * 0.04, galaxy['petroth90'] * 0.02), min_pixelscale) for galaxy in catalog]
# catalog['pixscale'] = [max(galaxy['petroth50'] * 0.04, min_pixelscale) for galaxy in catalog]

pixscale_data = catalog[(catalog['pixscale'] < 0.5) & (catalog['pixscale'] > min_pixelscale)]['pixscale']
plt.hist(pixscale_data, bins=50)
plt.savefig('joint_catalog_pixscale_dist.png')

n_min_limit = (catalog['pixscale'] == min_pixelscale).sum()
n_above_native = (catalog['pixscale'] > 0.262).sum()
print('{} ({})  galaxies at min pixscale'.format(n_min_limit, n_min_limit/len(catalog)))
print('{} ({})  galaxies above native pixscale'.format(n_above_native, n_above_native/len(catalog)))
