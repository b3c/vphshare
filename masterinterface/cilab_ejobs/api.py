__author__ = 'Miguel C.'
import base64
from django.db.models import Q
from permissions.models import PrincipalRoleRelation
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate, getUserTokens
from masterinterface.scs_auth import models
import models as M

from permissions.models import Role
from permissions.utils import get_roles

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
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,"producer")

            if uid:
                try:
                    # TODO now this user can submit a job
                    M.ejob_submit(uid,0,"")
                    return { "username": uname }

                except M.EJobException, e:
                    logger.exception(e)
                    return rc.FORBIDDEN

            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN


    def read(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,"producer")

            if uid:
                try:
                    # TODO if user can get tasks
                    # get tasks from db
                    return { "username": uname }

                except M.EJobException, e:
                    logger.exception(e)
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN

    def update(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,"consumer")

            if uid:
                try:
                    # TODO now this user can submit a job
                    M.ejob_transit(0,uid,"")
                    return { "username": uname }
                except M.EJobException, e:
                    logger.exception(e)
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN


    def delete(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,"producer")

            if uid:
                # TODO now this user can submit a job
                M.ejob_cancel(0,uid)
                return { "username": uname }
            else:
                return rc.FORBIDDEN
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

    except Exception, e:
        logger.exception(e)
        ticket = None

    finally:
        logger.debug( "checked ticket for %s" %(ticket[1],) )
        return ticket

def _get_id_and_check_tokens(uname,token_name):
    """get _id if token_name in user tokens else None
    """
    user = models.User.objects.get(username=uname)
    if user is not None:
        tokens = getUserTokens(user)
        logger.debug( "getid and check tokens %s" % (str(tokens),) )

        if (token_name in tokens):
            logger.debug("user with correct token")
            return user.id
        else:
            logger.debug("feiled to check token in set")
            return None
    else:
        logger.debug("failed to get id")
        return None

