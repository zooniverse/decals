
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog


def apply_selection_cuts(input_catalog, snap_tolerance=1e-3):
    """
    Select only galaxies with petrotheta > 3 and not within 1e-3 of bad measurement snap value

    Args:
        catalog (astropy.Table): Galaxy catalog including NSA information
        snap_tolerance (float): Minimum deviation from bad measurement snap value allowed

    Returns:
        (astropy.Table) catalog of galaxies matching selection criteria above

    """

    # Galaxies should be sufficiently extended across the sky
    petrotheta_above_3 = input_catalog['petrotheta'] > 3

    # NSA catalog’s petrotheta calculation sometimes fails to a ‘default’ value
    # Any galaxies with petrotheta within 1e-3 of the snap_to value likely has the wrong size.
    bad_petrotheta_value = 27.653702  # this 'magic' value can be confirmed by looking at petrotheta histograms
    snap_lower_limit = bad_petrotheta_value - snap_tolerance
    snap_upper_limit = bad_petrotheta_value + snap_tolerance

    above_snap_lower_limit = input_catalog['petrotheta'] > snap_lower_limit
    below_snap_upper_limit = input_catalog['petrotheta'] < snap_upper_limit
    within_snap_window = above_snap_lower_limit & below_snap_upper_limit

    selected_catalog = input_catalog[petrotheta_above_3 & ~ within_snap_window]
    return selected_catalog


def visualise_bad_petrotheta_measurements(nsa):
    """
    Save histograms of petrotheta, demonstrating the snap value problem

    Args:
        nsa (astropy.Table): NSA catalog of galaxies

    Returns:
        None
    """
    nsa_small = nsa[nsa['petrotheta'] < 50]
    plt.hist(nsa_small['petrotheta'], bins=100)
    plt.ylabel('Count')
    plt.xlabel('Petrotheta for NSA galaxies according to catalog')
    plt.savefig('petrotheta_hist.png')

    plt.clf()
    nsa_wrong = nsa[(nsa['petrotheta'] > 26) & (nsa['petrotheta'] < 29)]
    plt.hist(nsa_wrong['petrotheta'], bins=40)
    plt.ylabel('Count')
    plt.xlabel('Petrotheta for NSA galaxies according to catalog')
    plt.savefig('petrotheta_hist_28.png')

    print(pd.Series(nsa_wrong['petrotheta']).value_counts())


if __name__ == '__main__':
    # save figures of the petrotheta measurement problem
    nsa_version = '1_0_0'
    nsa_catalog_loc = '/data/galaxy_zoo/decals/catalogs/nsa_v1_0_0.fits'
    nsa = get_nsa_catalog(nsa_catalog_loc, nsa_version)
    visualise_bad_petrotheta_measurements(nsa)
