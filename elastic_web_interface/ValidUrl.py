from collections import defaultdict, Counter
import re
import os
import json

try:
        # For python 2
            from urlparse import urlparse, parse_qs
except ImportError:
        # For python 3
        from urllib.parse import urlparse, parse_qs

filter_string = ""
for line in open("./elastic_web_interface/static/filter.txt", "r"):
    filter_string += line
JSON_FILTER = json.loads(filter_string)

# Helpers
def path_valid(url_path):
    if (url_path == '/'):
	return True 
    split_path = url_path.split("/")
    path_count = Counter(split_path)
    for word in path_count:
	if (word != "") and (path_count[word] > 1):
	    return False
    return True

class ValidUrl():
    def __init__(self):
        self.url = ''

    def is_valid(self, url):
        '''
        Function returns True or False based on whether the url has to be downloaded or not.
        Robot rules and duplication rules are checked separately.
        This is a great place to filter out crawler traps.
        '''
        global JSON_FILTER
        url = url.encode('ascii', 'ignore')
        parsed = urlparse(url)
        valid_url = True 
        for invalid_path in JSON_FILTER['paths']:
            if (invalid_path in parsed.path.lower()):
                #print "Path issue: path: ", parsed.path
                valid_url = False
        for invalid_char in JSON_FILTER['invalid_chars']:
            if invalid_char in parsed.geturl().lower():
                #print "Character issue: url: ", parsed.geturl()
                valid_url = False
        for invalid_query in JSON_FILTER['query']:
            if invalid_query in parsed.query.lower():
                #print "Query issue: url: ", parsed.geturl()
                valid_url = False
        if (((parsed.netloc.lower() + parsed.path.lower()) == 'http://archive.ics.uci.edu/ml/datasets.html') and (parsed.query == '')):
            valid_url = False
        elif ((parsed.hostname != None) and (parsed.hostname.lower() in JSON_FILTER['subdomains'])):
            #print "Subdomain issue: subdomain: ", parsed.hostname
            valid_url = False
        elif (re.search('/', parsed.query)):
            #print "Query issue: query: ", parsed.query
            valid_url = False
        elif (parsed.scheme not in JSON_FILTER['schemes']):
            #print "Scheme issue: scheme", parsed.scheme
            valid_url = False
        elif (not path_valid(parsed.path)):
            #print "Failed path_valid function (duplicate words in path): ", parsed.path
            valid_url = False
        elif (".ics.uci.edu" not in parsed.hostname.lower()):
            #print ".ics.uci.edu not in parsed hostname: ", parsed.hostname
            valid_url = False
        elif (not re.search('edu$', parsed.netloc.lower()) or (not re.search('^/', parsed.path))):
            valid_url = False
        try:
            if (re.match(".*\." + JSON_FILTER['filetypes'] + "$", parsed.path.lower())):
                #print "Filetype issue"
                valid_url = False
        except TypeError:
            print ("TypeError for ", parsed)
            valid_url = False
        
        print "Parsed URL: ", parsed, " VALID? ", valid_url
        if (not valid_url):
            return False
        else:
            return True
