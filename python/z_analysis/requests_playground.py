import requests

fits_loc = '/data/fits.fits'
url = 'http://legacysurvey.org/viewer/fits-cutout?ra=147.176446949&dec=-0.354030416643&pixscale=0.1432296&size=424&layer=decals-dr5'

result = requests.get(url, stream=True)
open(fits_loc, 'wb').write(result.content)
