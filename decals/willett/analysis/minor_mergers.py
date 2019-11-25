# How many galaxies with signs of minor mergers are there in the DECaLS data?

from astropy.io import fits

filename = "/Users/willettk/Astronomy/Research/GalaxyZoo/gz_reduction_sandbox/data/full_decals/decals_weighted_unseeded_collated_01_wdup.fits"

data = fits.getdata(filename,1)

# Can't be star or artifact

not_artifact = data['t00_smooth_or_features_a2_artifact_weighted_frac'] < 0.2

# At least N weighted votes for any category that wasn't "neither"

c_arr = []
b_arr = []
m_arr = []
t_arr = []

votearr = range(5,41)

for mv in votearr:
    merger_votes = (1. - data['t09_merging_tidal_debris_a3_neither_weighted_frac']) * data['t09_merging_tidal_debris_weighted'] > float(mv)

    candidates = data[not_artifact & merger_votes]
    
    both = candidates['t09_merging_tidal_debris_a2_both_weighted_frac']
    merging = candidates['t09_merging_tidal_debris_a0_merging_weighted_frac']
    td = candidates['t09_merging_tidal_debris_a1_tidal_debris_weighted_frac']
    
    bc = sum((both >= merging) & (both >= td))
    mc = sum((merging >= both) & (merging >= td))
    tc = sum((td >= merging) & (td >= both))
    
    #print "{0} possible mergers/tidal debris images.".format(len(candidates))
    #print "{0} identified as merger.".format(mc)
    #print "{0} identified as tidal debris.".format(tc)
    #print "{0} identified as both merger AND tidal debris.".format(bc)

    b_arr.append(bc)
    m_arr.append(mc)
    t_arr.append(tc)
    c_arr.append(len(candidates))

from matplotlib import pyplot as plt

fig,axarr = plt.subplots(nrows=1,ncols=2,figsize=(12,6))

ax1,ax2 = axarr.ravel()

ax1.plot(votearr,c_arr,lw=3,color='k',label='Total candidates')
ax1.plot(votearr,m_arr,lw=3,label = 'Merging')
ax1.plot(votearr,t_arr,lw=3,label = 'Tidal debris')
ax1.plot(votearr,b_arr,lw=3,label = 'Both')

ax1.legend(fontsize=10)
ax1.set_xlabel('Minimum number of votes in T09',fontsize=16)
ax1.set_ylabel('Candidates',fontsize=16)

m_frac = [x * 1./y for x,y in zip(m_arr,c_arr)]
t_frac = [x * 1./y for x,y in zip(t_arr,c_arr)]
b_frac = [x * 1./y for x,y in zip(b_arr,c_arr)]
  
ax2.plot(votearr,m_frac,lw=3,label = 'Merging')
ax2.plot(votearr,t_frac,lw=3,label = 'Tidal debris')
ax2.plot(votearr,b_frac,lw=3,label = 'Both')

ax2.legend(loc='best',fontsize=10)
ax2.set_ylim(0,1)
ax2.set_xlabel('Minimum number of votes in T09',fontsize=16)
ax2.set_ylabel('Fraction of total merger candidates',fontsize=16)


fig.tight_layout()
plt.savefig('../plots/minor_mergers.pdf')

# Statistics for the "clean" cutoff, just for clarity

merger_votes = (1. - data['t09_merging_tidal_debris_a3_neither_weighted_frac']) >= 0.8
clean = data[not_artifact & merger_votes]

both = candidates['t09_merging_tidal_debris_a2_both_weighted_frac']
merging = candidates['t09_merging_tidal_debris_a0_merging_weighted_frac']
td = candidates['t09_merging_tidal_debris_a1_tidal_debris_weighted_frac']

bc = sum((both >= merging) & (both >= td))
mc = sum((merging >= both) & (merging >= td))
tc = sum((td >= merging) & (td >= both))

print "{0} possible mergers/tidal debris images.".format(len(candidates))
print "{0} identified as merger.".format(mc)
print "{0} identified as tidal debris.".format(tc)
print "{0} identified as both merger AND tidal debris.".format(bc)


# How does it change if I move from unweighted to weighted data?
