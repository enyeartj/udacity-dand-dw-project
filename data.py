# -*- coding: utf-8 -*-
"""
Created on Sat Mar 05 10:19:19 2016

@author: John Enyeart
"""
import re
import json
import codecs
from pprint import pprint
import xml.etree.cElementTree as ET

# local imports
from osmREs import zipCodeRE, problemChars, streetWordSwitches, streetNameSwitches

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def processStreetName(name):
    # remove punctuation
    name = re.sub('[\.,]','',name)
    
    # fix full street name issues found in audit
    for switch in streetNameSwitches:
        name = switch(name)
    
    # fix abbreviations, etc. in individual words of street name
    words = name.split(' ')
    fixedWords = []
    for word in words:
        for switch in streetWordSwitches:
            word = switch(word)
        fixedWords.append(word)
    name = ' '.join(fixedWords)
    
    return name

def processTag(tagkeybase, splittag, tagval, node):
    # if it's not in node, add it
    if tagkeybase not in node:
        if len(splittag) == 1:
            # if there are no 'sub' tags, then assign value to tag key in node
            node[tagkeybase] = tagval
        else:
            # if there are 'sub' tags, they need to be added to a dictionary
            node[tagkeybase] = {splittag[1] : tagval}
    else:
        # what we're doing here is making or appending a list if the value
        # for the node key is a single value or a list. if the key is already
        # in the node, but the value isn't a dictionary and a dictionary needs
        # to be added (or vice versa), the original value and the new
        # dictionary are put into a list
        if type(node[tagkeybase]) != dict:
            if type(node[tagkeybase]) == list:
                if len(splittag) == 1:
                    node[tagkeybase].append(tagval)
                else:
                    added = False
                    for item in node[tagkeybase]:
                        if type(item) == dict:
                            item[splittag[1]] = tagval
                            added = True
                            break
                    if not added:
                        node[tagkeybase].append({splittag[1] : tagval})
            else:
                if len(splittag) == 1:
                    node[tagkeybase] = [node[tagkeybase], tagval]
                else:
                    node[tagkeybase] = [node[tagkeybase], {splittag[1] : tagval}]
        else:
            if len(splittag) == 1:
                node[tagkeybase] = [node[tagkeybase], tagval]
            else:
                node[tagkeybase][splittag[1]] = tagval
    return node

def shape_element(element):
    node = {'created' : {}}
    # process only 2 types of top level tags: "node" and "way"
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        # attributes for latitude and longitude should be added to a "pos"
        # array, for use in geospacial indexing. Make sure the values inside
        # "pos" array are floats and not strings.
        if 'lat' in element.attrib.keys() and 'lon' in element.attrib.keys():
            node['pos'] = [float(element.attrib['lat']),
                           float(element.attrib['lon'])]
        for key, value in element.items():
            # attributes in the CREATED array should be added under a key "created"
            if key in CREATED:
                node['created'][key] = value
                continue
            if key in ['lat', 'lon']:
                continue
            node[key] = value
        
        for tag in element.iter("tag"):
            tagkey = tag.attrib['k']
            tagval = tag.attrib['v']
            splittag = tagkey.split(':')
            tagkeybase = splittag[0]
            # right now, I will only process tag keys to two levels
            # i.e. "addr:street" will be processed, but "addr:street:name" wont
            if len(splittag) > 2:
                continue
            
            # if the second level tag "k" value contains problematic
            # characters, it should be ignored
            if problemChars.search(tagkey):
                continue
            
            # fix street names
            if is_street_name(tag):
                tagval = processStreetName(tagval)
            
            # clean up zip codes
            if 'postcode' in tagkey and not zipCodeRE.search(tagval):
                # get rid of the 'NV 89123' and 'Nevada 89123' types
                if len(tagval.split(' ')) > 1:
                    tagval = tagval.split(' ')[-1]
                # fix the single case that came out in audit of u'89123\u200e'
                if tagval == u'89123\u200e':
                    tagval = '89123'
            
            if tagkeybase == 'addr':
                node = processTag('address', splittag, tagval, node)
            else:
                node = processTag(tagkeybase, splittag, tagval, node)
        
        if element.tag == "way":
            node['node_refs'] = []
            for nd in element.iter("nd"):
                node['node_refs'].append(nd.attrib['ref'])
        return node
    else:
        return None

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def insert_data(jsonfile):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.osmproject
    data = []
    with open(jsonfile) as f:
        for line in f.readlines():
            data.append(json.loads(line))
    db.las_vegas.insert_many(data)
    pprint(db.las_vegas.find_one())
    return db

if __name__ == '__main__':
#    data = process_map('las-vegas_nevada.osm')
#    pprint(data[0])
    db = insert_data('las-vegas_nevada.osm.json')