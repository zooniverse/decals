# General settings for to_zooniverse

zooniverse_login_loc = '/home/mike/repos/decals/python/b_to_zooniverse/do_upload/zooniverse_login.txt'

catalog_dir = '/media/mike/beta/decals/catalogs'

subject_loc = '/data/galaxy_zoo/decals/subjects/decals_dr1_and_dr2.csv'
previous_subjects_loc = '/data/galaxy_zoo/decals/subjects/galaxy_zoo_subjects.csv'  # DR1 and DR2 subjects
nsa_v1_0_0_catalog_loc = f'{catalog_dir}/nsa_v1_0_0.fits'  # only used to fill in DR1/DR2 metadata

nsa_version = '1_0_0'  # to select which joint catalog
data_release = '5'

nsa_catalog_loc = f'{catalog_dir}/nsa_v{nsa_version}.fits'
nsa_cached_loc = f'{catalog_dir}/nsa_v{nsa_version}_cached_for_upload.fits'

joint_catalog_loc = f'{catalog_dir}/dr{data_release}_nsa_v{nsa_version}_to_upload.fits'
expert_catalog_loc = f'{catalog_dir}/nair_sdss_catalog.fit'
expert_catalog_interpreted_loc = f'{catalog_dir}/nair_sdss_catalog_interpreted.csv'

# only calibration_dir and the files that joint catalog point to are on external drives
calibration_dir = '/Volumes/alpha/decals/png_native/calibration'
