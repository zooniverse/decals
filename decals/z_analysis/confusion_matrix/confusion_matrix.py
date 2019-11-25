
import pandas as pd

from pymongo import MongoClient

from astropy.table import Table
from astropy.io import fits

# expert_catalog_loc = '/data/galaxy_zoo/decals/catalogs/nair_expert_sdss_catalog.fit'
#
# catalog = Table(fits.getdata(expert_catalog_loc))
#
# expert = catalog.to_pandas()
# expert.loc[:, 'iauname'] = expert['SDSS'].apply(lambda x: x[:-1])
#
# galaxy_zoo_with_nsa = pd.read_csv('/data/galaxy_zoo/decals/catalogs/galaxy_zoo_decals_with_nsa_v1_0_0.csv')
#
# print(expert['iauname'])
# print(galaxy_zoo_with_nsa['iauname'])
# expert_with_galaxy_zoo = pd.merge(expert, galaxy_zoo_with_nsa, on='iauname', how='inner')
#
# print(expert_with_galaxy_zoo.iloc[0])
# print(len(expert_with_galaxy_zoo))
# # 10% match rate, seems quite low?
#
# expert_zooniverse_id = expert_with_galaxy_zoo.iloc[0]['zooniverse_id']
expert_zooniverse_id = 'AGZ000cnvm'

client = MongoClient()
db = client.galaxy_zoo

classifications = db.classifications

classifications_with_id = classifications.find({'subjects':
                                                    {'$elemMatch':
                                                        {'zooniverse_id': expert_zooniverse_id}
                                                     }
                                                })


for classification in classifications_with_id:
    print(classification)

all_annotations = [classification['annotations'] for classification in classifications_with_id[:4]]


def clean_annotations(annotations_list):
    """

    Args:
        annotations (list): list of dicts e.g. [{lang: eng}, {decals-1: a-0}]

    Returns:
        (pd.Series)

    """

    annotations = {}
    for annotations_dict in annotations_list:
        annotations.update(annotations_dict)

    try:
        del annotations['lang']
    except:
        pass
    for key, value in annotations.items():
        if type(value) == list:
            del annotations[key]
    return annotations


def all_annotations_to_predictions(all_annotations):
    df = pd.DataFrame([clean_annotations(x) for x in all_annotations])
    print(df)

all_annotations_to_predictions(all_annotations)
