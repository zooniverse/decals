import pytest

import json

import numpy as np
import pandas as pd
from astropy.table import Table

from b_to_zooniverse.previous_subjects.previous_decals_subjects import link_previous_subjects_with_nsa, get_previous_decals_subjects


@pytest.fixture()
def decals_subjects():
    return pd.DataFrame([
        # DR1 entries have provided_image_id filled with iau name, nsa_id blank, dr blank
        {'_id': 'ObjectId(0)',
         'zooniverse_id': 'gz_a',
         'provided_image_id': 'iau_a',
         'nsa_id': np.nan,
         'dr': np.nan
         },


        # DR2 entries have provided_image_id blank, nsa_id filled with NSA_[number], dr filled with 'DR2'
        {'_id': 'ObjectId(1)',
         'zooniverse_id': 'gz_b',
         'provided_image_id': np.nan,
         'nsa_id': 'NSA_1',
         'dr': 'DR2'
         }
    ])


@pytest.fixture()
def galaxy_zoo_subjects():
    return pd.DataFrame([
        # DR1 entries have provided_image_id filled with iau name, nsa_id blank, dr blank
        {'_id': 'ObjectId(0)',
         'zooniverse_id': 'gz_a',
         'group_id': 'group_id_a',
         'metadata': json.dumps({
             'survey': 'decals',
             'provided_image_id': 'iau_a',
             'counters': {'feature': 0,
                          'smooth': 0,
                          'star': 0}})
         },


        # DR2 entries have provided_image_id blank, nsa_id filled with NSA_[number], dr filled with 'DR2'
        {'_id': 'ObjectId(1)',
         'zooniverse_id': 'gz_b',
         'group_id': 'group_id_b',
         'metadata': json.dumps({
             'nsa_id': 'NSA_1',
             'dr': 'DR2',
             'counters': {'feature': 0,
                          'smooth': 0,
                          'star': 0}})
         },
    ])


@pytest.fixture()
def nsa():
    return Table([

        {'iauname': 'iau_a',
         'nsa_id': '0',
         'ra': 10.,
         'dec': -1.,
         'nsa_version': '1_0_0'},

        {'iauname': 'iau_b',
         'nsa_id': '1',
         'ra': 10.,
         'dec': -1.,
         'nsa_version': '1_0_0'}
    ])


def test_get_galaxy_zoo_decals_catalog_with_nsa(decals_subjects, nsa):
    galaxy_zoo_with_nsa = link_previous_subjects_with_nsa(decals_subjects, nsa)

    target_df = pd.DataFrame([
        {'zooniverse_id': 'gz_a',
         '_id': 'ObjectId(0)',
         'data_release': 'DR1',
         'dec': -1.0,
         'iauname': 'iau_a',
         'nsa_id': 0,
         'ra': 10.0},

        {'zooniverse_id': 'gz_b',
         '_id': 'ObjectId(1)',
         'data_release': 'DR2',
         'dec': -1.0,
         'iauname': 'iau_b',
         'nsa_id': 1,
         'ra': 10.0},
    ]).set_index('zooniverse_id', drop=True)

    # there should be no duplicated b_to_zooniverse ids (there will
    assert not any(galaxy_zoo_with_nsa.index.duplicated())

    # more descriptive errors than df1.equals(df2)
    for zooniverse_id in galaxy_zoo_with_nsa.index:
        for column in galaxy_zoo_with_nsa.columns.values:
            assert galaxy_zoo_with_nsa.loc[zooniverse_id][column] == target_df.loc[zooniverse_id][column]


def test_get_previous_decals_subjects(galaxy_zoo_subjects, nsa):
    galaxy_zoo_subjects.to_csv('fake_subjects.csv')
    cleaned_decals_subjects = get_previous_decals_subjects(galaxy_zoo_subjects, nsa)
    print(cleaned_decals_subjects)