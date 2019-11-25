from pymongo import MongoClient

import pandas as pd

client = MongoClient()
db = client.galaxy_zoo

subjects = db.subjects
classifications = db.classifications

# cursor = subjects.find({'classification_count': 40})
# cursor = subjects.find({'metadata.survey': 'decals'})

# cursor = subjects.find({'metadata.dr': 'DR2'})
#
# for document in cursor[:10]:
#     print(document)

    # metadata = document['metadata']
    # print(metadata)
    # print(metadata['provided_image_id'])
    # print(metadata['dr'])
    # print(document['location']['standard'])

# get previous decals classifications by zooniverse id
# match classification <- zoo id -> nsa using galaxy zoo with nsa code

# load expert catalog

classification = classifications.find_one()
zooniverse_id = classification['subjects'][0]['zooniverse_id']
print(zooniverse_id)

classifications_of_id = classifications.find({'subjects': [zooniverse_id]})
for single_classification in classifications_of_id:
    print(single_classification)

subjects_with_id = subjects.find({'zooniverse_id': zooniverse_id})
for single_subject in subjects_with_id:
    print(single_subject)

# cursor = classifications.find({'metadata.dr': 'DR2'})
# cursor = subjects.find({'metadata.survey': 'candels'})

# for document in cursor[:1]:
#
#     print(document['annotations'])
#     for subject in document['subjects']:
#         print(subject['zooniverse_id'])
#         print(subject['metadata'])

# subjects = subjects.find({'metadata.dr': 'DR2'})
# for subject in subjects[:1]:
#     classifications_of_subject = classifications.find()