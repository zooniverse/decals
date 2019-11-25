path = '/Users/willettk/Astronomy/Research/GalaxyZoo/decals'
volpath = '/Volumes/3TB/gz4/DECaLS/jpeg/standard'

import os
import random
import shutil

from astropy.io import fits

# Various task recipes for getting the morphological categories in the new DECaLS tree

task = {'t01_smooth_or_features_a01_smooth':0.80,'label':'smooth'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'label':'features'}
task = {'t01_smooth_or_features_a03_star_or_artifact':0.80,'label':'artifact'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a04_yes':0.80,'label':'edgeon'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80,'label':'not_edgeon'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't03_bar_a06_bar':0.80,'label':'bar'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't03_bar_a07_no_bar':0.80,'label':'no_bar'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'label':'spiral'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a09_no_spiral':0.80,'label':'no_spiral'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't05_bulge_prominence_a10_no_bulge':0.10,'t05_bulge_prominence_a11_just_noticeable':0.80, \
        'label':'no_bulge'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't05_bulge_prominence_a12_obvious':0.80, 'label':'obvious_bulge'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't05_bulge_prominence_a13_dominant':0.30, 'label':'dominant_bulge'}
task = {'t01_smooth_or_features_a01_smooth':0.80,'t07_rounded_a16_completely_round':0.80, \
        'label':'completely_round'}
task = {'t01_smooth_or_features_a01_smooth':0.80,'t07_rounded_a17_in_between':0.80, \
        'label':'in_between'}
task = {'t01_smooth_or_features_a01_smooth':0.80,'t07_rounded_a18_cigar_shaped':0.50, \
        'label':'cigar_shaped'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a19_ring':0.50, \
        'label':'ring'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a20_lens_or_arc':0.50, \
        'label':'lens'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a22_irregular':0.75, \
        'label':'irregular'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a23_other':0.75, \
        'label':'other'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a24_merger':0.75, \
        'label':'merger'}
task = {'t06_odd_a14_yes':0.50,'t08_odd_feature_a38_dust_lane':0.50, \
        'label':'dustlane'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80, \
        't02_edgeon_a04_yes':0.80,'t09_bulge_shape_a25_rounded':0.80,'label':'bulge_round'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.50, \
        't02_edgeon_a04_yes':0.50,'t09_bulge_shape_a26_boxy':0.40,'label':'bulge_boxy'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.50, \
        't02_edgeon_a04_yes':0.50,'t09_bulge_shape_a27_no_bulge':0.40,'label':'bulge_none'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t10_arms_winding_a28_tight':0.80,'label':'arms_tight'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t10_arms_winding_a29_medium':0.70,'label':'arms_medium'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t10_arms_winding_a30_loose':0.70,'label':'arms_loose'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t11_arms_number_a31_1':0.50,'label':'arms_1'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t11_arms_number_a32_2':0.80,'label':'arms_2'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t11_arms_number_a33_3':0.80,'label':'arms_3'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t11_arms_number_a34_4':0.50,'label':'arms_4'}
task = {'t01_smooth_or_features_a02_features_or_disk':0.80,'t02_edgeon_a05_no':0.80, \
        't04_spiral_a08_spiral':0.80,'t11_arms_number_a36_more_than_4':0.50,'label':'arms_5plus'}

def load_data():

    data = fits.getdata('%s/decals_gz2.fits' % path,1)

    return data

def copy_examples(data):

    for k in task:
        if k != 'label':
            data = data[data['%s_debiased' % k] > task[k]]

    exampledir = '%s/examples/%s' % (path,task['label'])
    if not os.path.exists(exampledir):
        os.makedirs(exampledir)

    N = 100
    if len(data) > N:
        datasamp = random.sample(data,N)
    else:
        datasamp = data
        print 'Only %i examples of %s' % (len(data),task['label'])
    for gal in datasamp:
        shutil.copy('%s/%s_standard.jpeg' % (volpath,gal['IAUNAME']),'%s/%s.jpeg' % (exampledir,gal['IAUNAME']))

    return None
