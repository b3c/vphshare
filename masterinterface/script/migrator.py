__author__ = 'm.balasso@scsitaly.com'


import os
from physiomespace import DataResource
from msf import create_msf_from_tree

from config import *

print "\nWELCOME TO THE PHYSIOMESPACE MIGRATION SAMPLE APP\n"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print "-- Output Directory Created\n"
else:
    print "-- Output Directory already exists!\n"


print "-- Downloading tree xmls\n"
root = DataResource(USERNAME, PASSWORD, ROOT_ID, REPOSITORY_ID, PS_URL)
print root.pretty_print()
print "-- Done!\n"

print "-- Downloading binaries..."
root.download(OUTPUT_DIR)
print "\n-- Done!\n"

print "\n-- Creating msf file"
create_msf_from_tree(root, os.path.join(OUTPUT_DIR, '%s.msf' % ROOT_ID))
print "-- Done!\n"

print "\nBye bye!"