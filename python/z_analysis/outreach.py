
from astropy.table import Table

from a_download_decals import download_decals_settings as settings


def main():

    joint_catalog = Table.read(settings.upload_catalog_loc, overwrite=True)
    joint_catalog

if __name__ == '__main__':
    main()
