__author__ = 'Miguel C.'
import base64
from django.db.models import Q
from permissions.models import PrincipalRoleRelation
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
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
    This feature needs a cron job removing jobs completed|cancelled older than 1 day
    python manage.py migrate cilab_ejobs to migrate to db
    python manage.py schemamigration cilab_ejobs --auto to update model changes
    """
    allowed_methods = ('POST', 'GET', 'PUT', 'DELETE')

    def create(self, request, *args, **kwargs):
        """the post method to post a job into the queue.

            no uri args but you have to post with params
            data the input data (json dict) to include into the job with
            at least 3 fields: {"message":"task message","data":{"what":"ever dict"},"worker_id":124}
        """
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer"]))

            if uid:
                try:
                    input_data = json.loads(str(request.body))
                    worker_id = input_data.get("worker_id",-1)
                    o = M.ejob_submit(uid,worker_id,input_data)
                    return o

                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST

            else:
                logger.error("ejob failed to get id and check tokens")
                return rc.FORBIDDEN
        else:
            logger.error("ejob failed to check ticket")
            return rc.FORBIDDEN


    def read(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer","consumer"]))

            if uid:
                try:
                    #get from only one task with id global_id
                    if global_id:
                        try:
                            l = M.EJob.objects.get(Q(id__exact=global_id),
                                                Q(owner_id__exact=uid) | Q(worker_id__exact=uid) )

                            #r = serializers.serialize("json",l)
                            return l
                        except Exception, e:
                            logger.exception(e)
                            return rc.NOT_FOUND

                    #get a list of tasks
                    else:
                        l = M.EJob.objects.filter(Q(owner_id__exact=uid) | Q(worker_id__exact=uid) )
                        return l

                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN

    def update(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["consumer"]))

            if uid:
                try:
                    # TODO now this user can submit a job
                    M.ejob_transit(0,uid,"")
                    return { "username": uname }
                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN


    def delete(self, request, global_id=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer"]))

            oid = int(global_id if global_id else -1)
            if uid and (oid > -1):
                try:
                    # TODO change to transition
                    o = M.ejob_cancel(oid,uid)
                    return o
                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST
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

def _get_id_and_check_tokens(uname,token_set):
    """get _id if token_set in user tokens else None
    """
    user = models.User.objects.get(username=uname)
    if user is not None:
        tokens = getUserTokens(user)
        logger.debug( "getid and check tokens %s" % (str(tokens),) )

        if (len(tokens.intersection(token_set)) > 0):
            logger.debug("user with correct token")
            return user.id
        else:
            logger.debug("feiled to check token in set")
            return None
    else:
        logger.debug("failed to get id")
        return None

