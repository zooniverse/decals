# Temporarily here

import matplotlib.pyplot as plt

from a_download_decals.get_catalogs.get_joint_nsa_decals_catalog import get_nsa_catalog, get_decals_bricks

data_release = '5'

catalog_dir = '/data/galaxy_zoo/decals/catalogs'

nsa_version = '0_1_2'
nsa_catalog_loc = '{}/nsa_v{}.fits'.format(catalog_dir, nsa_version)
nsa_0 = get_nsa_catalog(nsa_catalog_loc)

nsa_version = '1_0_0'
nsa_catalog_loc = '{}/nsa_v{}.fits'.format(catalog_dir, nsa_ver¡sion)
nsa_1 = get_nsa_catalog(nsa_catalog_loc)


bricks_filename = 'survey-bricks-dr{}-with-coordinates.fits'.format(data_release)
bricks_loc = '{}/{}'.format(catalog_dir, bricks_filename)
bricks = get_decals_bricks(bricks_loc, data_release)

print(len(nsa_0))
print(len(nsa_1))

print(nsa_0.colnames)
print(nsa_1.colnames)

print(nsa_0['ra'].min(), nsa_0['ra'].mean(), nsa_0['dec'].max())
print(nsa_1['ra'].min(), nsa_1['ra'].mean(), nsa_1['dec'].max())

print(nsa_0['z'].min(), nsa_0['z'].mean(), nsa_0['z'].max())
print(nsa_1['z'].min(), nsa_1['z'].mean(), nsa_1['z'].max())

print(nsa_0['petrotheta'].min(), nsa_0['petrotheta'].mean(), nsa_0['petrotheta'].max())
print(nsa_1['petrotheta'].min(), nsa_1['petrotheta'].mean(), nsa_1['petrotheta'].max())

plt, axes = plt.subplots(2, sharex=True, sharey=True)
_, bins, _ = axes[1].hist(nsa_1['z'])
axes[1].set_title('nsa_1_0_0')
axes[1].set_ylabel('galaxy count')
axes[1].set_xlabel('redshift')
axes[0].hist(nsa_0['z'], bins=bins)
axes[0].set_ylabel('galaxy count')
axes[0].set_title('nsa_0_1_2')
plt.tight_layout()
plt.savefig('nsa_atlas_galaxies_by_redshift')

# nsa_0_filtered = nsa_0[(nsa_0['petrotheta'] > 3.)]
# nsa_1_filtered = nsa_1[(nsa_1['petrotheta'] > 3.) & (nsa_1['z'] < 0.055)]
# print(len(nsa_0_filtered))
# print(len(nsa_1_filtered))
# #
# nsa_0_sample = nsa_0_filtered[np.random.rand(len(nsa_0_filtered)) > 0.97]
# nsa_1_sample = nsa_1_filtered[np.random.rand(len(nsa_1_filtered)) > 0.99]
#
# print(len(bricks), 'bricks length')
# bricks_sample = bricks[np.random.rand(len(bricks)) > 0.9]
#
# plt.figure()
# plt.scatter(nsa_0_sample['ra'], nsa_0_sample['dec'], alpha=0.5)
# plt.scatter(nsa_1_sample['ra'], nsa_1_sample['dec'], alpha=0.5)
# plt.xlabel('ra')
# plt.ylabel('dec')
# plt.legend(['0_1_2', '1_0_1'])
# plt.tight_layout()
# plt.savefig('nsa_atlas_coverage_comparison.png')
#
# plt.figure()
# plt.scatter(nsa_0_sample['ra'], nsa_0_sample['dec'], alpha=0.5)
# plt.scatter(nsa_1_sample['ra'], nsa_1_sample['dec'], alpha=0.5)
# plt.scatter(bricks_sample['ra'], bricks_sample['dec'], alpha=0.5)
# plt.xlabel('ra')
# plt.ylabel('dec')
# plt.tight_layout()
# plt.legend(['0_1_2', '1_0_1', 'DECALS'])
# plt.savefig('nsa_bricks_coverage_comparison.png')
