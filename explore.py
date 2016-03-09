# -*- coding: utf-8 -*-
"""
Created on Sun Mar 06 20:19:00 2016

@author: John Enyeart
"""

from pprint import pprint
from pymongo import MongoClient, GEO2D

client = MongoClient("mongodb://localhost:27017")
db = client.osmproject

# how many places of worship do each religion have?
religionPipeline = [
    { "$match" : { "amenity" : { "$exists" : 1 },
                   "amenity" : "place_of_worship",
                   "religion" : { "$exists" : 1 } } },
    { "$group" : { "_id" : "$religion",
                   "count" : { "$sum" : 1 } } },
    { "$sort" : { "count" : -1 } }
]

amenityPipeline = [
    { "$match" : { "amenity" : { "$exists" : 1 },
                   "amenity" : "place_of_worship",
                   "religion" : { "$exists" : 1 } } },
    { "$group" : { "_id" : "$religion",
                   "count" : { "$sum" : 1 } } },
    { "$sort" : { "count" : -1 } }
]

top10ZipCodePipeline = [
    { "$match" : { "address.postcode" : { "$exists" : 1 } } },
    { "$group" : { "_id" : "$address.postcode",
                   "count" : { "$sum" : 1 } } },
    { "$sort" : { "count" : -1 } },
    { "$limit" : 10 }
]

top10RestaurantPipeline = [
    { "$match" : { "amenity" : "restaurant" } },
    { "$group" : { "_id" : "$name",
                   "count" : { "$sum" : 1 } } },
    { "$sort" : { "count" : -1 } },
    { "$limit" : 10 }
]

def getResult(pipeline):
    return db.las_vegas.aggregate(pipeline)

def countWebsites():
    return db.las_vegas.find({ "website" : { "$exists" : 1 } }).count()

def setUpGeoSpatialIndex():
    db.las_vegas.ensure_index([("pos", GEO2D)])

def findRestaurantsNearRangerStation():
    loc = db.las_vegas.find_one({ "amenity" : "ranger_station" })['pos']
    result = db.las_vegas.find({
        "pos" : { "$near" : loc },
        "amenity" : "restaurant",
        "name" : { "$exists" : 1 }
    })
    
    return result[:10]

if __name__ == '__main__':
#    result = getResult(religionPipeline)
#    result = getResult(amenityPipeline)
#    result = getResult(top10ZipCodePipeline)
#    result = getResult(top10RestaurantPipeline)
    result = findRestaurantsNearRangerStation()
    pprint([r for r in result])