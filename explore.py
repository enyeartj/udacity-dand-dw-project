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
def getReligions():
    result = db.las_vegas.aggregate([
        { "$match" : { "amenity" : { "$exists" : 1 },
                       "amenity" : "place_of_worship",
                       "religion" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$religion",
                       "count" : { "$sum" : 1 } } },
        { "$sort" : { "count" : -1 } }
    ])
    
    return result

def countAmenities():
    result = db.las_vegas.aggregate([
        { "$match" : { "amenity" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$amenity",
                       "count" : { "$sum" : 1 } } },
        { "$sort" : { "count" : -1 } }
    ])
    
    return result

def top10ZipCodes():
    result = db.las_vegas.aggregate([
        { "$match" : { "address.postcode" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$address.postcode",
                       "count" : { "$sum" : 1 } } },
        { "$sort" : { "count" : -1 } },
        { "$limit" : 10 }
    ])
    
    return result

def top10Restaurants():
    result = db.las_vegas.aggregate([
        { "$match" : { "amenity" : "restaurant" } },
        { "$group" : { "_id" : "$name",
                       "count" : { "$sum" : 1 } } },
        { "$sort" : { "count" : -1 } },
        { "$limit" : 10 }
    ])
    
    return result

def countWebsites():
    return db.las_vegas.find({ "website" : { "$exists" : 1 } }).count()

def setUpGeoSpatialIndex():
    db.las_vegas.ensure_index([("pos", GEO2D)])

def findRestaurantsNearRangerStation():
    loc = db.las_vegas.find_one({ "amenity" : "ranger_station" })['pos']
    result = db.las_vegas.aggregate([
        { "$geoNear" : { "near" : { "type" : "Point", "coordinates" : loc },
                         "distanceField" : "dist.calculated",
                         "maxDistance" : 2 } },
        { "$match" : { "amenity" : "restaurant" } },
        { "$group" : { "_id" : "$name" } }
    ])
    
    return result

if __name__ == '__main__':
#    result = getReligions()
#    result = top10ZipCodes()
#    result = top10Restaurants()
#    result = countAmenities()
    result = findRestaurantsNearRangerStation()
    pprint([r for r in result])