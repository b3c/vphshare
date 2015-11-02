__author__ = 'Miguel C.'
from django.db.models import Q
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate, getUserTokens
from masterinterface.scs_auth import models
import models as M

from piston.utils import rc
# import the logging library
import logging

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
            at least 3 fields: {"message":"task message",
                                "data":{"what":"ever dict"},
                                "worker_id":-1,
                                "worker_name":"el1mc",
                                "auto_run":true}
        """
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer"]))

            if uid:
                try:
                    input_data = json.loads(str(request.body))
                    worker_id = input_data.get("worker_id",-1)
                    worker_name = input_data.get("worker_name","")

                    # trying to get worker_name if worker_id -1
                    # then using worker_name try if has role and get id
                    if worker_id == -1 and worker_name:
                        wid = _get_id_and_check_tokens(worker_name,set(["consumer"]))
                        worker_id = wid if wid is not None else -1

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
        """the read method to get a job <global_id> or all jobs from the queue.

            You will get elements limited to your role (producer|consumer)
        """
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer","consumer"]))

            if uid:
                try:
                    #get from only one task with id global_id
                    if global_id:
                        try:
                            l = M.ejob_get_gte_one(uid, uid, global_id)
                            return l

                        except Exception, e:
                            logger.exception(e)
                            return rc.NOT_FOUND

                    #get a list of tasks
                    else:
                        l = M.ejob_get_gte_one(uid, uid)
                        return l

                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN

    def update(self, request, global_id=None,  *args, **kwargs):
        """the opdate method to put a job from the queue.

            global_id the job to modify
            json body data (json dict) with information about what to modify
            at least 1 fields: {"state": (>=1,!=2),"data":{"what":"ever dict"}}
            the data field can be optional but only used when transits to done
        """
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["consumer"]))

            oid = int(global_id if global_id else -1)
            input_data = json.loads(str(request.body))

            if uid and (oid > -1):
                try:
                    o = M.ejob_transit(oid,uid,input_data)
                    return o

                except Exception, e:
                    logger.exception(e)
                    return rc.BAD_REQUEST
            else:
                return rc.FORBIDDEN
        else:
            return rc.FORBIDDEN


    def delete(self, request, global_id=None,  *args, **kwargs):
        """delete method to transit a ejob to cancelled.

        You have to be the producer to do this
        """
        ticket = _check_header_ticket(request)

        if ticket is not None:
            uname = ticket[1]
            uid = _get_id_and_check_tokens(uname,set(["producer"]))

            oid = int(global_id if global_id else -1)
            if uid and (oid > -1):
                try:
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

