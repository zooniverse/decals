# Do some preliminary analysis on the results of the DECaLS-Galaxy Zoo data. 

import re
from collections import Counter

import numpy as np
import pandas as pd
from astropy.cosmology import WMAP9
from astropy.io import fits
from gz_class import plurality
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm

gzpath = '/Users/willettk/Astronomy/Research/GalaxyZoo'
decals_path = '{0}/decals'.format(gzpath)
plot_path = '{0}/plots'.format(decals_path)

"""

decals_analysis
=========

Make plots and start analysis on the collated Galaxy Zoo-DECaLS data.

Kyle Willett (UMN) - 10 Dec 2015

"""

def load_data():

    mgs = fits.getdata('{0}/matched/gz2_main.fits'.format(decals_path),1)
    s82 = fits.getdata('{0}/matched/gz2_s82_coadd1.fits'.format(decals_path),1)
    decals = fits.getdata('{0}/matched/decals_dr1.fits'.format(decals_path),1)

    return mgs,s82,decals

def color_mag_plots(mgs,s82,decals,savefig=False):

    # Make paneled histograms of the color distribution for several magnitude bins of Galaxy Zoo data.

    """
    SDSS main sample (GZ2)
    Stripe 82 coadded data (GZ2)
    DECaLS
    """

    redshifts = (0.12,0.08,0.05)
    appmag_lim = 17.0
    # Work out the magnitude limit from cosmology

    fig,axarr = plt.subplots(num=1,nrows=3,ncols=3,figsize=(12,10))

    for z,ax in zip(redshifts,axarr.ravel()):
        absmag_lim = appmag_lim - WMAP9.distmod(z).value
        maglim = (mgs['PETROMAG_MR'] < absmag_lim) & (mgs['REDSHIFT'] <= z)
        spiral = mgs['t01_smooth_or_features_a02_features_or_disk_weighted_fraction'] >= 0.8
        elliptical = mgs['t01_smooth_or_features_a01_smooth_weighted_fraction'] >= 0.8
        ax.hist(mgs[maglim & spiral]['PETROMAG_U'] - mgs[maglim & spiral]['PETROMAG_R'],range=(0,4),bins=25,color='blue',histtype='step',label='spiral')
        ax.hist(mgs[maglim & elliptical]['PETROMAG_U'] - mgs[maglim & elliptical]['PETROMAG_R'],range=(0,4),bins=25,color='red',histtype='step',label='elliptical')

        ax.set_xlabel(r'$(u-r)$',fontsize=16)
        ax.set_title(r'$M_r<{0:.2f}, z<{1:.2f}$'.format(absmag_lim,z),fontsize=16)
        ax.text(0.95,0.95,'MGS',ha='right',va='top',transform=ax.transAxes)

        if ax == axarr.ravel()[0]:
            ax.legend(loc='upper left',fontsize=10)

    s82_lim = 17.77
    for z,ax in zip(redshifts,axarr.ravel()[3:6]):
        absmag_lim = s82_lim - WMAP9.distmod(z).value
        maglim = (s82['PETROMAG_MR'] < absmag_lim) & (s82['REDSHIFT'] <= z)
        spiral = s82['t01_smooth_or_features_a02_features_or_disk_weighted_fraction'] >= 0.8
        elliptical = s82['t01_smooth_or_features_a01_smooth_weighted_fraction'] >= 0.8
        ax.hist(s82[maglim & spiral]['PETROMAG_U'] - s82[maglim & spiral]['PETROMAG_R'],range=(0,4),bins=25,color='blue',histtype='step',label='spiral')
        ax.hist(s82[maglim & elliptical]['PETROMAG_U'] - s82[maglim & elliptical]['PETROMAG_R'],range=(0,4),bins=25,color='red',histtype='step',label='elliptical')

        ax.set_xlabel(r'$(u-r)$',fontsize=16)
        ax.set_title(r'$M_r<{0:.2f}, z<{1:.2f}$'.format(absmag_lim,z),fontsize=16)
        ax.text(0.95,0.95,'Stripe 82',ha='right',va='top',transform=ax.transAxes)

    decals_lim = 17.77
    for z,ax in zip(redshifts,axarr.ravel()[6:]):
        absmag_lim = decals_lim - WMAP9.distmod(z).value
        maglim = (decals['metadata.mag.abs_r'] < absmag_lim) & (decals['metadata.redshift'] <= z)
        spiral = decals['t00_smooth_or_features_a1_features_frac'] >= 0.8
        elliptical = decals['t00_smooth_or_features_a0_smooth_frac'] >= 0.8
        ax.hist(decals[maglim & spiral]['metadata.mag.u'] - decals[maglim & spiral]['metadata.mag.r'],range=(0,4),bins=25,color='blue',histtype='step',label='spiral')
        ax.hist(decals[maglim & elliptical]['metadata.mag.u'] - decals[maglim & elliptical]['metadata.mag.r'],range=(0,4),bins=25,color='red',histtype='step',label='elliptical')

        ax.set_xlabel(r'$(u-r)$',fontsize=16)
        ax.set_title(r'$M_r<{0:.2f}, z<{1:.2f}$'.format(absmag_lim,z),fontsize=16)
        ax.text(0.95,0.95,'DECaLS',ha='right',va='top',transform=ax.transAxes)

    fig.tight_layout()
    if savefig:
        plt.savefig('{0}/color_hist.pdf'.format(plot_path))
    else:
        plt.show()

    return None

def color_mag_ratio(mgs,s82,decal,savefig=False):

    # Plot the spiral to elliptical ratio as a function of optical color.

    redshifts = (0.12,0.08,0.05)
    linestyles = ('solid','dashed','dashdot')

    datasets = ({'data':mgs,
                 'title':'MGS',
                 'appmag':17.0,
                 'sp':'t01_smooth_or_features_a02_features_or_disk_weighted_fraction',
                 'el':'t01_smooth_or_features_a01_smooth_weighted_fraction',
                 'umag':'PETROMAG_U',
                 'rmag':'PETROMAG_R',
                 'absr':'PETROMAG_MR',
                 'redshift':'REDSHIFT'},
                {'data':s82,
                 'title':'Stripe 82',
                 'appmag':17.77,
                 'sp':'t01_smooth_or_features_a02_features_or_disk_weighted_fraction',
                 'el':'t01_smooth_or_features_a01_smooth_weighted_fraction',
                 'umag':'PETROMAG_U',
                 'rmag':'PETROMAG_R',
                 'absr':'PETROMAG_MR',
                 'redshift':'REDSHIFT'},
                {'data':decals,
                 'title':'DECaLS',
                 'appmag':17.77,
                 'sp':'t00_smooth_or_features_a1_features_frac',
                 'el':'t00_smooth_or_features_a0_smooth_frac',
                 'umag':'metadata.mag.u',
                 'rmag':'metadata.mag.r',
                 'absr':'metadata.mag.abs_r',
                 'redshift':'metadata.redshift'})

    # Work out the magnitude limit from cosmology

    fig,axarr = plt.subplots(num=2,nrows=1,ncols=3,figsize=(12,5))

    for ax,d in zip(axarr.ravel(),datasets):
        for z,ls in zip(redshifts,linestyles):
            absmag_lim = d['appmag'] - WMAP9.distmod(z).value
            maglim = (d['data'][d['absr']] < absmag_lim) & (d['data'][d['redshift']] <= z)
            spiral = d['data'][d['sp']] >= 0.8
            elliptical = d['data'][d['el']] >= 0.8
            n_sp,bins_sp = np.histogram(d['data'][maglim & spiral][d['umag']] - d['data'][maglim & spiral][d['rmag']],range=(0,4),bins=25)
            n_el,bins_el = np.histogram(d['data'][maglim & elliptical][d['umag']] - d['data'][maglim & elliptical][d['rmag']],range=(0,4),bins=25)

            plotval = np.log10(n_sp * 1./n_el)
            ax.plot(bins_sp[1:],plotval,linestyle=ls,label=r'$M_r<{0:.2f}, z<{1:.2f}$'.format(absmag_lim,z))

        ax.set_xlabel(r'$(u-r)$',fontsize=16)
        ax.set_ylabel(r'$\log(n_{sp}/n_{el})$',fontsize=16)
        ax.set_ylim(-1.5,1.5)
        ax.set_title(d['title'],fontsize=16)
        if ax == axarr.ravel()[0]:
            ax.legend(loc='upper left',fontsize=8)

    fig.tight_layout()
    
    if savefig:
        plt.savefig('{0}/feature_ratio.pdf'.format(plot_path))
    else:
        plt.show()

    return None

def feature_comparison(savefig=False):

    # Plot the difference in vote fractions for the matched galaxies

    filename = '{0}/fits/decals_gz2_union.fits'.format(decals_path)

    data = fits.getdata(filename,1)

    # Map the columns
    matched_cols = [{'title':'smooth',                   'gz2':"gz2_t01_smooth_or_features_a01_smooth_fraction",             "decals":"decals_t00_smooth_or_features_a0_smooth_frac"},
                    {'title':'features/disk',            'gz2':"gz2_t01_smooth_or_features_a02_features_or_disk_fraction",   "decals":"decals_t00_smooth_or_features_a1_features_frac"},
                    {'title':'star',                     'gz2':"gz2_t01_smooth_or_features_a03_star_or_artifact_fraction",   "decals":"decals_t00_smooth_or_features_a2_artifact_frac"},
                    {'title':'edge-on',                  'gz2':"gz2_t02_edgeon_a04_yes_fraction",                            "decals":"decals_t01_disk_edge_on_a0_yes_frac"},
                    {'title':'not edge-on',              'gz2':"gz2_t02_edgeon_a05_no_fraction",                             "decals":"decals_t01_disk_edge_on_a1_no_frac"},
                    {'title':'bar',                      'gz2':"gz2_t03_bar_a06_bar_fraction",                               "decals":"decals_t02_bar_a0_bar_frac"},
                    {'title':'no bar',                   'gz2':"gz2_t03_bar_a07_no_bar_fraction",                            "decals":"decals_t02_bar_a1_no_bar_frac"},
                    {'title':'spiral',                   'gz2':"gz2_t04_spiral_a08_spiral_fraction",                         "decals":"decals_t03_spiral_a0_spiral_frac"},
                    {'title':'no spiral',                'gz2':"gz2_t04_spiral_a09_no_spiral_fraction",                      "decals":"decals_t03_spiral_a1_no_spiral_frac"},
                    {'title':'no bulge',                 'gz2':"gz2_t05_bulge_prominence_a10_no_bulge_fraction",             "decals":"decals_t04_bulge_prominence_a0_no_bulge_frac"},
                    {'title':'medium bulge',             'gz2':"gz2_t05_bulge_prominence_a11_just_noticeable_fraction",      "decals":"decals_t04_bulge_prominence_a1_obvious_frac"},
                    {'title':'obvious bulge',            'gz2':"gz2_t05_bulge_prominence_a12_obvious_fraction",              "decals":"decals_t04_bulge_prominence_a2_dominant_frac"},
                    {'title':'completely round',         'gz2':"gz2_t07_rounded_a16_completely_round_fraction",              "decals":"decals_t08_rounded_a0_completely_round_frac"},
                    {'title':'in between',               'gz2':"gz2_t07_rounded_a17_in_between_fraction",                    "decals":"decals_t08_rounded_a1_in_between_frac"},
                    {'title':'cigar shaped',             'gz2':"gz2_t07_rounded_a18_cigar_shaped_fraction",                  "decals":"decals_t08_rounded_a2_cigar_shaped_frac"},
                    {'title':'ring',                     'gz2':"gz2_t08_odd_feature_a19_ring_fraction",                      "decals":"decals_t10_odd_feature_x1_ring_frac"},
                    {'title':'lens/arc',                 'gz2':"gz2_t08_odd_feature_a20_lens_or_arc_fraction",               "decals":"decals_t10_odd_feature_x2_lens_frac"},
                    {'title':'irregular',                'gz2':"gz2_t08_odd_feature_a22_irregular_fraction",                 "decals":"decals_t10_odd_feature_x4_irregular_frac"},
                    {'title':'other',                    'gz2':"gz2_t08_odd_feature_a23_other_fraction",                     "decals":"decals_t10_odd_feature_x5_other_frac"},
                    {'title':'dust lane',                'gz2':"gz2_t08_odd_feature_a38_dust_lane_fraction",                 "decals":"decals_t10_odd_feature_x3_dustlane_frac"},
                    {'title':'rounded bulge',            'gz2':"gz2_t09_bulge_shape_a25_rounded_fraction",                   "decals":"decals_t07_bulge_shape_a0_rounded_frac"},
                    {'title':'boxy bulge',               'gz2':"gz2_t09_bulge_shape_a26_boxy_fraction",                      "decals":"decals_t07_bulge_shape_a1_boxy_frac"},
                    {'title':'no bulge',                 'gz2':"gz2_t09_bulge_shape_a27_no_bulge_fraction",                  "decals":"decals_t07_bulge_shape_a2_no_bulge_frac"},
                    {'title':'tight arms',               'gz2':"gz2_t10_arms_winding_a28_tight_fraction",                    "decals":"decals_t05_arms_winding_a0_tight_frac"},
                    {'title':'medium arms',              'gz2':"gz2_t10_arms_winding_a29_medium_fraction",                   "decals":"decals_t05_arms_winding_a1_medium_frac"},
                    {'title':'loose arms',               'gz2':"gz2_t10_arms_winding_a30_loose_fraction",                    "decals":"decals_t05_arms_winding_a2_loose_frac"},
                    {'title':'1 arm',                    'gz2':"gz2_t11_arms_number_a31_1_fraction",                         "decals":"decals_t06_arms_number_a0_1_frac"},
                    {'title':'2 arms',                   'gz2':"gz2_t11_arms_number_a32_2_fraction",                         "decals":"decals_t06_arms_number_a1_2_frac"},
                    {'title':'3 arms',                   'gz2':"gz2_t11_arms_number_a33_3_fraction",                         "decals":"decals_t06_arms_number_a2_3_frac"},
                    {'title':'4 arms',                   'gz2':"gz2_t11_arms_number_a34_4_fraction",                         "decals":"decals_t06_arms_number_a3_4_frac"},
                    {'title':'5+ arms',                  'gz2':"gz2_t11_arms_number_a36_more_than_4_fraction",               "decals":"decals_t06_arms_number_a4_more_than_4_frac"}]

    # Working, but still needs to sort for questions that are ACTUALLY ANSWERED. Lots of pileup at 0,0.
    columns = data.columns

    decals_fraccols,gz2_fraccols = [],[]
    for c in columns:
        colname = c.name
        if len(colname) > 6:
            if colname[-4:] == 'frac' and colname[:6] == 'decals':
                decals_fraccols.append(c)
        if len(colname) > 17:
            if colname[-8:] == 'fraction' and colname[-17:] != "weighted_fraction" and colname[:3] == 'gz2':
                gz2_fraccols.append(c)

    decals_votearr = data.from_columns(decals_fraccols)
    gz2_votearr = data.from_columns(gz2_fraccols)

    decals_tasks,gz2_tasks = [],[]
    for v in decals_votearr:
        e_decals,a_decals = plurality(np.array(list(v)),'decals') 
        decals_tasks.append(e_decals)
    for v in gz2_votearr:
        e_gz2,a_gz2 = plurality(np.array(list(v)),'gz2') 
        gz2_tasks.append(e_gz2)


    fig,axarr = plt.subplots(num=1,nrows=4,ncols=8,figsize=(16,10))
    nrows = axarr.shape[0]
    ncols = axarr.shape[1]

    def plot_features(ax,taskno,indices):
        plotind = indices.flatten()
        ax.hist2d(data[matched_cols[taskno]['gz2']][plotind],data[matched_cols[taskno]['decals']][plotind],bins=(20,20),range=[[0,1],[0,1]],norm=LogNorm(),cmap = cm.viridis)
        ax.plot([0,1],[0,1],linestyle='--',color='red',lw=2)
        ax.set_title(matched_cols[taskno]['title'],fontsize=8)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.set_xlabel(r'$f_{GZ2}$',fontsize=10)
        ax.set_ylabel(r'$f_{DECaLS}$',fontsize=10)
        ax.set_aspect('equal')

    # Smooth/features
    answers_per_task = [3,2,2,2,3,3,5,3,3,5]
    match_tasks = [[ 0, 0],
                   [ 1, 1],
                   [ 2, 2],
                   [ 3, 3],
                   [ 4, 4],
                   [ 6, 8],
                   [ 7,10],
                   [ 8, 7],
                   [ 9, 5],
                   [10, 6]]

    n = 0
    for a,m in zip(answers_per_task,match_tasks):
        inds = np.array(([np.array(decals_tasks)[:,m[1]] == True])) & np.array(([np.array(gz2_tasks)[:,m[0]] == True]))
        for i in range(a):
            plot_features(axarr.ravel()[n],n,inds)
            n += 1

    '''
    for i in range(nrows):
        ax = axarr.ravel()[i*ncols]
        ax.set_ylabel(r'$f_{GZ2}$',fontsize=10)

    for i in range(ncols):
        ax = axarr.ravel()[(nrows - 1)*ncols + i]
        ax.set_xlabel(r'$f_{DECaLS}$',fontsize=10)
    '''

    for di in range((nrows*ncols)-n):
        fig.delaxes(axarr.ravel()[(nrows*ncols)-(di+1)])

    fig.tight_layout()
    if savefig:
        plt.savefig('{0}/decals_gz2_feature_comparison.pdf'.format(plot_path))
    else:
        plt.show()

    return None

def survey_dict():

    # Information about the specific group settings in the project

    d = {u'candels':        {'name':u'CANDELS','retire_limit':80},
        u'candels_2epoch':  {'name':u'CANDELS 2-epoch','retire_limit':80},
        u'decals':          {'name':u'DECaLS','retire_limit':40},
        u'ferengi':         {'name':u'FERENGI','retire_limit':40},
        u'goods_full':      {'name':u'GOODS full-depth','retire_limit':40},
        u'illustris':       {'name':u'Illustris','retire_limit':40},
        u'sloan_singleband':{'name':u'SDSS single-band','retire_limit':40},
        u'ukidss':          {'name':u'UKIDSS','retire_limit':40},
        #u'sloan':          {'name':u'SDSS DR8','retire_limit':60},
        u'stripe82':        {'name':u'Stripe 82','retire_limit':40},
        u'gz2':             {'name':u'SDSS DR7','retire_limit':40}}

    return d
    
def is_number(s):

    # Is a string a representation of a number?

    try:
        int(s)
        return True
    except ValueError:
        return False

def morphology_distribution(survey='decals'):

    # What's the plurality distribution of morphologies?
    
    try:
        collation_file = "{0}/gz_reduction_sandbox/data/decals_unweighted_classifications_00.csv".format(gzpath)
        collated = pd.read_csv(collation_file)
    except IOError:
        print "Collation file for {0:} does not exist. Aborting.".format(survey)
        return None

    columns = collated.columns

    fraccols,colnames = [],[]
    for c in columns:
        if c[-4:] == 'frac':
            fraccols.append(c)
        if c[0] == 't' and is_number(c[1:3]):
            colnames.append(c[:3])

    collist = list(set(colnames))
    collist.sort()

    # Plot distribution of vote fractions for each task

    ntasks = len(collist)
    ncols = 4 if ntasks > 9 else int(np.sqrt(ntasks))
    nrows = int(ntasks / ncols) if ntasks % ncols == 0 else int(ntasks / ncols) + 1

    sd = survey_dict()[survey]
    survey_name = sd['name']

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))] 

    tasklabels = f7([re.split("[ax][0-9]",f)[0][11:-1] for f in fraccols])
    labels = [re.split("[ax][0-9]",f)[-1][1:-5] for f in fraccols]

    # Make pie charts of the plurality votes

    votearr = np.array(collated[fraccols])
    class_arr,task_arr,task_ans = [],[],[]
    for v in votearr:
        e,a = plurality(v,survey) 
        task_arr.append(e)
        task_ans.append(a)

    task_arr = np.array(task_arr)
    task_ans = np.array(task_ans)

    fig,axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(15,12))

    colors=[u'#377EB8', u'#E41A1C', u'#4DAF4A', u'#984EA3', u'#FF7F00',u'#A6761D',u'#1B9E77']

    n = (task_arr.shape)[1]
    for i in range(n):
        ax = axarr.ravel()[i]
        c = Counter(task_ans[:,i][task_arr[:,i] == True])
        pv,pl = [],[]
        for k in c:
            pv.append(c[k])
            pl.append(labels[k])
        ax.pie(pv,labels=pl,colors=colors,autopct=lambda(p): '{:.0f}'.format(p * sum(pv) / 100))
        title = '{0:} - t{1:02} {2:}'.format(survey_name,i,tasklabels[i]) if i == 0 else 't{0:02} {1:}'.format(i,tasklabels[i])
        ax.set_title(title)
        ax.set_aspect('equal')

    # Remove empty axes from subplots
    if axarr.size > ntasks:
        for i in range(axarr.size - ntasks):
            ax = axarr.ravel()[axarr.size-(i+1)]
            ax.set_axis_off()

    fig.set_tight_layout(True)
    plt.savefig('{1}/decals/plots/pie_{0:}.eps'.format(survey,gzpath))
    plt.close()

    return None

def morph_table_gz2():

    # Print LaTeX-formatted tables of the GZ vote counts and fractions, and plot as pie chart.

    overlap = True
    survey = 'decals'

    # Get weights
    try:
        fitsfile = "{0}/dr10/dr10_gz2_main_specz.fits".format(gzpath)
        hdr = fits.getheader(fitsfile,1)
        colnames = []
        for i in range(hdr['TFIELDS']):
            colnames.append(hdr['TTYPE{0}'.format(i+1)])

        if overlap:
            if survey == 'gz2':
                collation_file = "{0}/decals/csv/decals_gz2_main.csv".format(gzpath)
            elif survey == 'stripe82':
                collation_file = "{0}/decals/csv/decals_gz2_stripe82c1.csv".format(gzpath)
            elif survey == 'decals':
                collation_file = "{0}/decals/csv/decals_gz2_union.csv".format(gzpath)
            collated = pd.read_csv(collation_file)
        else:
            if survey == 'gz2':
                collation_file = "{0}/dr10/dr10_gz2_main_specz.csv".format(gzpath)
            elif survey == 'stripe82':
                collation_file = "{0}/dr10/dr10_gz2_stripe82_coadd1.csv".format(gzpath)
            collated = pd.read_csv(collation_file,names=colnames)
    except IOError:
        print "Collation file for {0:} does not exist. Aborting.".format(survey)
        return None

    columns = collated.columns

    fraccols,colnames = [],[]
    if survey == 'decals':
        for c in columns:
            if len(c) > 10:
                if c[-4:] == 'frac' and c[:6] == 'decals':
                    fraccols.append(c)
                if c[7] == 't' and is_number(c[8:10]):
                    colnames.append(c[7:10])
    else:
        for c in columns:
            if c[-17:] == 'weighted_fraction':
                fraccols.append(c)
            if c[0] == 't' and is_number(c[1:3]):
                colnames.append(c[:3])

    collist = list(set(colnames))
    collist.sort()

    # Plot distribution of vote fractions for each task

    ntasks = len(collist)
    ncols = 4 if ntasks > 9 else int(np.sqrt(ntasks))
    nrows = int(ntasks / ncols) if ntasks % ncols == 0 else int(ntasks / ncols) + 1

    sd = survey_dict()[survey]
    survey_name = sd['name']

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))] 

    if survey == 'decals':
        tasklabels = f7([re.split("[ax][0-9]",f)[0][11:-1] for f in fraccols])
        labels = [re.split("[ax][0-9]",f)[-1][1:-5] for f in fraccols]
    else:
        tasklabels = f7([re.split("[ax][0-9]",f)[0][4:-1] for f in fraccols])
        labels = [re.split("[ax][0-9]",f[4:-18])[-1][2:] for f in fraccols]

    # Make pie charts of the plurality votes

    votearr = np.array(collated[fraccols])
    class_arr,task_arr,task_ans = [],[],[]
    for v in votearr:
        e,a = plurality(v,survey) 
        task_arr.append(e)
        task_ans.append(a)

    task_arr = np.array(task_arr)
    task_ans = np.array(task_ans)

    fig,axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(15,12))

    colors=[u'#377EB8', u'#E41A1C', u'#4DAF4A', u'#984EA3', u'#FF7F00',u'#A6761D',u'#1B9E77']

    n = (task_arr.shape)[1]
    for i in range(n):
        ax = axarr.ravel()[i]
        c = Counter(task_ans[:,i][task_arr[:,i] == True])
        pv,pl = [],[]
        task_total = sum(c.values())
        for k in c:
            pv.append(c[k])
            pl.append(labels[k])

            # Print to screen in LaTeX format
            print "{0:20} & {1:6} & {3:.2f} & {2:.2f}".format(labels[k],c[k],c[k] * 1./task_total,c[k] * 1./len(collated))
        print ""
        ax.pie(pv,labels=pl,colors=colors,autopct=lambda(p): '{:.0f}'.format(p * sum(pv) / 100))
        title = '{0:} - t{1:02} {2:}'.format(survey_name,i,tasklabels[i]) if i == 0 else 't{0:02} {1:}'.format(i,tasklabels[i])
        ax.set_title(title)
        ax.set_aspect('equal')

    # Remove empty axes from subplots
    if axarr.size > ntasks:
        for i in range(axarr.size - ntasks):
            ax = axarr.ravel()[axarr.size-(i+1)]
            ax.set_axis_off()

    fig.set_tight_layout(True)
    suffix = '_overlap' if overlap else ''
    plt.savefig('{1}/decals/plots/pie_{0}{2}.eps'.format(survey,gzpath,suffix))
    plt.close()

    return None

if __name__ == "__main__":

    mgs,s82,decals = load_data()
    #color_mag_plots(mgs,s82,decals,savefig=True)
    #color_mag_ratio(mgs,s82,decals,savefig=True)
    #feature_comparison(savefig=True)
