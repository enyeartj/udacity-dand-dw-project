# -*- coding: utf-8 -*-
"""
Created on Sat Mar 05 09:18:13 2016

@author: John Enyeart
"""

import re

streetWordReplacements = ( # meant for use on a single word
    ('^ave$', 'Avenue'),
    ('^st$', 'Street'),
    ('^s$', 'South'),
    ('^n$', 'North'),
    ('^w$', 'West'),
    ('^e$', 'East'),
    ('^pkwy$', 'Parkway'),
    ('^blvd$', 'Boulevard'),
    ('^rd$', 'Road'),
    ('^ln$', 'Lane'),
    ('^dr$', 'Drive'),
    ('^mt$', 'Mountain'),
    ('^ste$', 'Suite'),
    ('^pacific$', 'Pacific')
)

streetNameReplacements = ( # meant for entire street name string
    ('tropicana$', 'Tropicana Avenue'),
    ('sahara$', 'Sahara Avenue')
)

def buildSwitchFunction(search, replace):
    '''Builds a function to replace matches of search with replace in word.
    search is a regular expresion to match
    replace is a string that matches of search will be replaced with
    word is the (string) input to the generated function.
    '''
    def switch(word):
        return re.sub(search, replace, word, flags=re.IGNORECASE)
    return switch

streetWordSwitches = [buildSwitchFunction(search, replace)
    for (search, replace) in streetWordReplacements]

streetNameSwitches = [buildSwitchFunction(search, replace)
    for (search, replace) in streetNameReplacements]

streetTypeRE = re.compile(r'''
            # don't match beginning of string
    \b      # matches empty string at beginning or end of word
    \S +    # matches any non-whitespace character
    \.?     # matches 0 or 1 periods
    $       # end of string
    ''', (re.IGNORECASE | re.VERBOSE))

zipCodeRE = re.compile(r'''
    ^       # match beginning of string
    89      # Las Vegas zip codes all start with 89
    \d{3}   # for the other 3 digits
    (?:     # grouping for ZIP+4
    [-\s]   # match a space or a hyphen
    \d{4}   # match 4 digits
    )?      # the ZIP+4 grouping is optional
    $       # end of string
    ''', re.VERBOSE)

lower = re.compile(r'^([a-z]|_)*$')
lowerColon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemChars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')