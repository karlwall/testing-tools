#! /usr/bin/env python

"""
Reports differences between the industries in the datastore and the yaml files
in repo.

"""


import csv
import os
import re
import subprocess
import sys
import tempfile
import urllib2

import yaml



VERTICAL = "core_vertical"
INDUSTRY = "core_industry"



def main():
    """Main function."""
    try:
        server = sys.argv[1]
        repo = sys.argv[2]
        google_appengine_path = sys.argv[3]
    except IndexError:
        usage()
        return 1
    prepare()
    download(server, google_appengine_path)
    verticals = load_data()
    check(repo, verticals)
    return 0

def prepare():
    """
    Prepare environment.

    """
    # bulkloader.py won't overwrite files.
    for kind in (INDUSTRY, VERTICAL):
        path = _get_csv_path(kind)
        if os.path.exists(path):
            os.remove(path)

def download(server, google_appengine_path):
    """
    Downloads data from the app engine datastore and writes to .csv files.

    """
    for kind in (VERTICAL, INDUSTRY):
        args = ["python", 
                "%s" % os.path.join(google_appengine_path, "bulkloader.py"),
                "--config_file=bulkloader.yaml",
                "--download", 
                "--url=http://%s/_ah/remote_api/" % server,
                "--filename=%s" % _get_csv_path(kind),
                "--kind=%s" % kind,
                "--namespace=-global-"] 
        # run command
        rcode = subprocess.call(args)
        if rcode != 0:
            raise IOError("Download failed for kind %s" % kind)
    return

def load_data():
    """
    Loads data from .csv files into dictionary.

    """
    # Build keys: vertical csv file has columns: name, key.
    map_ = {}
    data = {}
    reader = csv.reader(open(_get_csv_path(VERTICAL), "rb"))
    reader.next()        # Ignore header row
    for row in reader:
        data[row[0]] = []
        map_[row[1]] = row[0]    # Map id to name
    # Industry csv file has columns: name, key, vertical_id.
    reader = csv.reader(open(_get_csv_path(INDUSTRY), "rb"))
    reader.next()
    for row in reader:
        key = map_[row[2]]
        data[key].append(row[0])
    return data

def check(repo, verticals):
    """
    Checks that expected yaml files exist, and that they can be loaded by the
    yaml module.

    Does not attempt to check that the data is valid for the bOnline
    application.

    """
    for vertical in verticals:
        for industry in verticals[vertical]:
            url = _get_yaml_url(repo, vertical, industry)
            try:
                response = urllib2.urlopen(url)
            except urllib2.URLError as ex:
                print "Attempt to fetch yaml file for vertical %s industry %s failed" % (vertical, industry)
                print "URL was %s" % url
                print "Exception was: %s" % ex
                try:
                    print "Status code was %d" % ex.code
                except AttributeError:
                    pass
                break
            try:
                yaml.load(response.read())
            except yaml.YAMLError as ex:
                print "Attempt to load yaml file for vertical %s industry %s failed" % (vertical, industry)
                print "%s" % ex
                break
    return




def usage():
    """Usage message. """
    print >> sys.stderr, "Usage: %s AppEngineServer StaticRepository PathToGoogleAppEngineSDK" % __file__




def _get_csv_path(name):
    """Gets path to csv file for kind. """
    return os.path.join(tempfile.gettempdir(), "%s" % (name + ".csv"))

def _get_yaml_url(repo, vertical, industry):
    """Builds url of yaml file in static repository. """
    folder = slugify(unicode(vertical))
    filename = slugify(unicode(industry)) + ".yaml"
    return "http://%s/static/industries/%s/%s" % (repo, folder, filename)


# 
# The slugify function is taken from django.template.defaultfilter.py
# as django may not be in sys.path
#
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)



if __name__ == "__main__":
    sys.exit(main())
