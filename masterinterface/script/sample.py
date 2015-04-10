__author__ = 'm.balasso@scsitaly.com'

import os
from physiomespace import DataResource, PrivateRepository
from msf import create_msf_from_tree

from config import *

users = ['testi']


for user in users:
    output_dir = os.path.join(BASE_DIR, user)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    repository = PrivateRepository('testi', 'debora')

    repository.download(output_dir)




