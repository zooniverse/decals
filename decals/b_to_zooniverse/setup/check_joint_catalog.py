import os

from astropy.table import Table

from shared_astro_utils import matching_utils, astropy_utils

from decals.a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog
import decals.b_to_zooniverse.to_zooniverse_settings as settings


def enforce_joint_catalog_columns(joint_catalog, overwrite_cache=False):
    """
    Make sure joint catalog has the required columns for Panoptes upload.
    If not, load the cached NSA catalog and add them.
    If no cached NSA catalog, make one.
    Args:
        joint_catalog (astropy.Table): NSA and DECALS galaxies. Potentially only including a column subset.
        overwrite_cache (bool): if True, always make a new NSA cache. If False, only make cache if none exists.

    Returns:
        (astropy.Table): joint catalog with all missing catalog columns added
    """

    # png_loc and fits_loc must have been added to joint catalog by this point by a downloader - raise error if not
    required_user_cols = [
        'png_loc',
        'fits_loc'
    ]
    for user_col in required_user_cols:
        assert user_col in set(joint_catalog.colnames)

    required_data_cols = [
        'nsa_id',
        'iauname',
        'ra',
        'dec',
        'petroth50',
        'petrotheta',
        'petroflux',
        'nsa_version',
        'z',
        'mag',
        'absmag',
        'nmgy',
    ]

    if set(required_data_cols) not in set(joint_catalog.colnames):
        print('Warning: joint catalog is missing columns: {}'.format(
            set(required_data_cols) - set(joint_catalog.colnames)))

        if not os.path.exists(settings.nsa_cached_loc) or overwrite_cache:
            print('No cache found - creating new cache at {}'.format(settings.nsa_cached_loc))
            kwargs = {'nsa_version': settings.nsa_version}
            astropy_utils.cache_table(
                settings.nsa_catalog_loc,
                settings.nsa_cached_loc,
                required_data_cols,
                get_nsa_catalog,  # loading func
                kwargs)

        cached_nsa = Table.read(settings.nsa_cached_loc)  # cached nsa table has already been through get_nsa_catalog

        # exclude columns not already included
        catalog_cols = joint_catalog.colnames
        nsa_cols = cached_nsa.colnames
        cached_nsa = cached_nsa[list(set(nsa_cols) - set(catalog_cols)) + ['ra', 'dec']]

        # add the missing data columns
        expanded_joint_catalog, _ = matching_utils.match_galaxies_to_catalog_table(joint_catalog, cached_nsa)

        assert len(expanded_joint_catalog) == len(joint_catalog)

        return expanded_joint_catalog
