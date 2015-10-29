__author__ = 'Miguel C.'
import base64
from django.db.models import Q
from permissions.models import PrincipalRoleRelation
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from piston.utils import rc
# import the logging library
import logging

import pickle
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

class EJobsAPIHandler(BaseHandler):
    """
    REST service based on Django-Piston Library
    """
    allowed_methods = ('POST', 'GET', 'PUT', 'DELETE')

    def create(self, request, *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            return { "username": ticket[1] }
        else:
            return rc.FORBIDDEN

    def read(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            return { "username": ticket[1] }
        else:
            return rc.FORBIDDEN

    def update(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            return { "username": ticket[1] }
        else:
            return rc.FORBIDDEN


    def delete(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            return { "username": ticket[1] }
        else:
            return rc.FORBIDDEN

def _check_header_ticket(req):
    """check header ticket
    """
    ticket = None

    try:
        client_address = req.META['REMOTE_ADDR']
        tkt = req.META.get('HTTP_MI_TICKET', '')
        if tkt:
            try:
                usr, tkt64 = authenticate(ticket=tkt, cip=client_address)
                ticket = (tkt,usr)

            except Exception:
                ticket = None
        else:
            ticket = None

    except Exception:
        client.captureException()
        ticket = None

    finally:
        return ticket

