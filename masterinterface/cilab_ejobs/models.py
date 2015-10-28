from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.db.models import Q
from django.http import HttpResponse
from permissions.models import PrincipalRoleRelation

from piston.handler import BaseHandler
from piston.utils import rc

from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs_resources.models import Resource

import base64
import json
import requests
from urlparse import urlparse
import itertools

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
