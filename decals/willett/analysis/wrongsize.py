from pymongo import MongoClient

# Find galaxies which are tagged in the mongodb output as 'wrong size'

client = MongoClient('localhost', 27017)

gz = client['galaxy_zoo'] 
subjects = gz['galaxy_zoo_subjects']

ouroboros = client['ouroboros']
discussions = ouroboros['discussions']

tags = ['wrongsize','wrong_size','imagesizewrong']
wstags = discussions.find({'comments.tags':{'$in':tags},'focus.type':'GalaxyZooSubject'})

zids = []
for tag in wstags:
    zids.append(tag['focus']['_id'])

surveys = []

# Check to see what survey groups these are attached to

surveys = []
for zid in zids:
    s = subjects.find_one({'zooniverse_id':zid})
    survey = s['metadata']['survey']

    if survey != 'decals':
        zids.remove(zid)
    surveys.append(survey)

# Print results to screen

from collections import Counter
print Counter(surveys)

with open("../csv/wrong_size.csv",'w') as f:
    for zid in zids:
        print >> f,zid
