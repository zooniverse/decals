[![Build Status](https://travis-ci.org/zooniverse/decals.svg?branch=master)](https://travis-ci.org/zooniverse/decals)
[![Maintainability](https://api.codeclimate.com/v1/badges/b9ab23a834c329d744b3/maintainability)](https://codeclimate.com/github/zooniverse/decals/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/b9ab23a834c329d744b3/test_coverage)](https://codeclimate.com/github/zooniverse/decals/test_coverage)
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)


# Decals

Morphological classifications for DECaLs DR5 by the Galaxy Zoo - DECaLS collaboration.

Written by Mike Walmsley.
Based on [previous work](https://github.com/willettk/decals)
by Kyle Willett and Coleman Krawcyzk for DR1 and DR2 respectively.

#### Aims

This repo collects the code related to the DECaLS classification project on Galaxy Zoo.
1. Identifying galaxies imaged in both SDSS and DECaLS
2. Downloading the telescope data
3. Creating RGB images for classification
4. Identifying galaxies not yet uploaded from DECaLS DR1 and DR2
5. Aggregating and interpreting the volunteer classifications

Currently (01.01.2018) aggregation (5) is only partially implemented

### Structure

The code is organised under /python into folders with the following aims:

+ a_download_decals
    - create a joint NSA/DECaLS catalog
    - save fits from the DECaLS cut-out server and create artistic jpeg
+ b_to_zooniverse
    - find previously uploaded DECaLS subjects
    - create a calibration catalog using Nair (2010)
    - create two jpeg versions of a fits image with different colouring
    - upload a catalog to Zooniverse Panoptes
+ c_from_zooniverse
    - download and aggregate Zooniverse Panoptes classifications
    - WIP!

Please see the README in each folder for instructions specific to each aim.

#### Files Required

1. The NASA-Sloan Atlas (NSA) catalog e.g. v1_0_1. Available from
SDSS DR13 [here](http://www.sdss.org/dr13/manga/manga-target-selection/nsa/) with schema [here](http://skyserver.sdss.org/dr13/en/help/browser/browser.aspx#&&history=description+nsatlas+U).
2. Brick (image tile) catalogs for DECaLS DR5. Available as two separate tables:
[survey-bricks.fits](http://portal.nersc.gov/project/cosmo/data/legacysurvey/dr5/survey-bricks.fits.gz) (all bricks) and [survey-bricks-dr5.fits](http://portal.nersc.gov/project/cosmo/data/legacysurvey/dr5/survey-bricks-dr5.fits.gz) (imaged bricks).
These tables are combined during setup.
Descriptions are [here](http://legacysurvey.org/dr5/files/).
3. All previous DECaLS Galaxy Zoo subjects and associated metadata.
All previous subjects are available as a .csv data dump on request to the Galaxy Zoo team.

More information is available about DECaLS DR5 [here](http://legacysurvey.org/dr5/).

#### Setup

The code involves quite a few files, and it needs to know where to look
 for or save each one.

To use the default settings, create the following directories.
Download the required files with the links above, and place them
in the directories as shown.

If you only want to download DR5:

+ catalogs (dir)
    - NSA_v1_0_1.fits.
    - survey-bricks.fits
    - survey-bricks-dr5.fits
+ subjects (dir)
    - galaxy_zoo_subjects.csv
+ fits (dir)
    + dr5 (dir)
+ jpeg (dir)
    + dr5 (dir)

Or, to enable downloading DR1, DR2 and DR5:

+ catalogs (dir)
    - NSA_v{e.g. 1_0_1}.fits
    - survey-bricks.fits
    - survey-bricks-dr5.fits
    - decals-bricks.fits
    - decals-bricks-dr1.fits
    - decals-bricks-dr2.fits
+ subjects (dir)
    - galaxy_zoo_subjects.csv
+ fits (dir)
    + dr5 (dir)
    + dr2 (dir)
    + dr1(dir)
+ jpeg (dir)
    + dr5 (dir)
    + dr2 (dir)
    + dr1(dir)

If you prefer to set up your own directories and filenames,
you can configure those settings (and all other settings) in the main file [here](https://github.com/zooniverse/decals/python/get_decals_images_and_catalogs.py).


#### Execution
Navigate to the repo root and run

`pip install -r requirements.txt`

This will install all required dependencies.
If you are using anaconda, you will already have most of them.
You must use Python 3.

Open python/get_decals_images_and_catalogs
1. Double-check all the filenames point where you've downloaded files
2. Choose the run configuration, as described inline.

Run unit tests if desired. From repo root directory:

`pytest`

To run each step, check the readme in the respective folder.


#### Known Issues

This code is under rapid development. Please check the Issues page before use.
