import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(PROJECT_ROOT)
sys.path.append( os.path.split(PROJECT_ROOT)[0] )

#os.environ["PYTHON_EGG_CACHE"] = "/tmp/.python-eggs"

from authentication import app as application
# set credential manager: BIOMEDTOWN or POSTGRES
CREDENTIAL_MANAGER='BIOMEDTOWN'

CREDENTIAL_MANAGER_URL="www.biomedtown.org"
