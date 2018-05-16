import astropy.table

from b_to_zooniverse.do_upload import manifest
from shared_utilities import current_date


def upload_galaxy_subject_set(catalog, subject_set_name):
    assert type(catalog) != str   # don't be stupid and mix up catalog with catalog name
    name = '{}_{}'.format(current_date(), subject_set_name)
    galaxy_manifest = manifest.create_manifest_from_joint_catalog(catalog)
    return manifest.upload_manifest_to_galaxy_zoo(name, galaxy_manifest)


def upload_nair_calibration_subject_set(calibration_catalog, subject_set_name, n_subjects=None):
    """
    Upload from the calibration catalog up to n_subjects/2 bars or rings, and n_subjects/2 others
    Color them with both DR2 style and Lupton style
    Args:
        calibration_catalog (astropy.Table): table of expertly classified galaxies, with nsa and decals info
        subject_set_name (str): name to give uploaded subject set on Panoptes. Must not already exist.
        n_subjects (int): total number of galaxies to upload, split evenly between featured (bar/ring) and other

    Returns:
        (astropy.Table): calibration subject set manifest, as uploaded to Panoptes
    """
    if n_subjects is None:
        n_subjects_per_class = len(calibration_catalog)  # don't slice, upload all
    else:
        n_subjects_per_class = int(n_subjects / 2)

    featured_galaxies = \
        calibration_catalog[calibration_catalog['has_bar'] | calibration_catalog['has_ring']][:n_subjects_per_class]
    other_galaxies = \
        calibration_catalog[~calibration_catalog['has_bar'] & ~calibration_catalog['has_ring']][:n_subjects_per_class]
    calibration_galaxies = astropy.table.vstack([featured_galaxies, other_galaxies])
    print('Calibration bars: {}'.format(featured_galaxies['has_bar'].sum()))
    print('Calibration rings: {}'.format(featured_galaxies['has_ring'].sum()))
    print('Calibration non-bar, non-ring: {}'.format(len(other_galaxies)))

    name = '{}_{}'.format(current_date(), subject_set_name)
    calibration_galaxies_manifest = manifest.create_manifest_from_joint_catalog(calibration_galaxies)
    manifest.upload_manifest_to_galaxy_zoo(name, calibration_galaxies_manifest)
