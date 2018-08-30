from datetime import datetime

from datetime import datetime

from pymongo import MongoClient

client = MongoClient()
db = client.primer
coll = db.dataset

# cursor = db.restaurants.find({"borough": "Manhattan"})
#
# for document in cursor:
#     print(document)

# cursor = db.restaurants.find({"grades.grade": "A"})
# cursor = db.restaurants.find({"grades.score": {"$gt": 0}})
cursor = db.restaurants.find({"cuisine": "Italian", "address.zipcode": "10075"})

for document in cursor:
    print(document)
