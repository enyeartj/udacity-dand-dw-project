# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 06:39:39 2016

@author: John Enyeart
"""

import xml.etree.cElementTree as ET
from pprint import pprint
from collections import defaultdict

# local imports
from osmREs import streetTypeRE, lower, lowerColon, problemChars

osm_filename = 'las-vegas_nevada.osm'

street_types = defaultdict(set)
baseTags = defaultdict(int)
zipCodes = defaultdict(set)
tigerZipCodes = defaultdict(set)
tiger_name_types = defaultdict(set)
users = set()
others = set()

EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Road",
            "Circle", "Highway", "Lane", "Parkway", "Trail", "Way"]

def key_type(element, keys):
    if element.tag == "tag":
        for tag in element.iter():
            if lower.search(tag.attrib['k']):
                keys['lower'] += 1
            elif lowerColon.search(tag.attrib['k']):
                keys['lower_colon'] += 1
            elif problemChars.search(tag.attrib['k']):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
                others.add(tag.attrib['k'])
        
    return keys

def audit_street_type(street_types, street_name):
    m = streetTypeRE.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in EXPECTED:
            street_types[street_type].add(street_name)

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_tiger_attrib(elem):
    return (elem.attrib['k'][:6] == 'tiger:')

def is_tiger_name_type(elem):
    return (elem.attrib['k'] == 'tiger:name_type')

def audit(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    with open(filename, 'r') as osm_file:
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            # get a count of all tags used
            baseTags[elem.tag] += 1
            
            # get unique user IDs ("uid")
            if 'uid' in elem.attrib:
                users.add(elem.attrib['uid'])
            
            # check for good tags, tags with colons, and problem tags
            keys = key_type(elem, keys)
            
            # audit ways and nodes
            if elem.tag == 'way' or elem.tag == 'node':
                for tag in elem.iter('tag'):
                    # get list of all unexpected street types
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])
                    if is_tiger_name_type(tag):
                        audit_street_type(tiger_name_types, tag.attrib['v'])
                    
                    # get zip codes
                    # note: only ways have tiger data and
                    # only tiger data has zip codes in this data set.
                    if 'tiger' in tag.attrib['k'] and ('zip' in tag.attrib['k'] or 'postcode' in tag.attrib['k']):
                        tigerZipCodes[tag.attrib['k']].add(tag.attrib['v'])
                    elif 'zip' in tag.attrib['k'] or 'postcode' in tag.attrib['k']:
                        zipCodes[tag.attrib['k']].add(tag.attrib['v'])
    return keys

if __name__ == '__main__':
    keys = audit(osm_filename)
#    pprint(dict(baseTags))
#    pprint(dict(zipCodes))
#    pprint(dict(tigerZipCodes))
#    pprint(dict(street_types))
#    pprint(dict(tiger_name_types))
#    pprint(keys)
#    pprint(others)
#    pprint(users)