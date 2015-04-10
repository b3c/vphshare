__author__ = 'm.balasso@scsitaly.com'

import os

ENCRYPTION = True
PS_URL = 'www.physiomespace.com'

# insert your ps credentials
USERNAME = 'testuser'
PASSWORD = '6w8DHF'

# the repository id to download from
REPOSITORY_ID = 'vphop-project'

# the root id you want to download
ROOT_ID = 'dataresource.2012-09-17.1347897253275'

# the base dir for testing
BASE_DIR = 'C:\\Users\\%s\\Desktop\\PSTestDownload\\' % (os.environ.get("USERNAME"))

# the output dir
OUTPUT_DIR = 'C:\\Users\\%s\\Desktop\\PSTestDownload\\%s' % (os.environ.get("USERNAME"), ROOT_ID)

# tha path to the botanApp binary
BOTAN_APP = "C:\\b3c_software\\PSLoader\\bin\\botanApp.exe"