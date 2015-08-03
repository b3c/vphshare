__author__ = 'Alfredo Saglimbeni, Ernesto Coto'
import base64
from django.db.models import Q
from permissions.models import PrincipalRoleRelation
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs_resources.forms import WorkflowForm
from masterinterface.scs_resources.models import Workflow
from masterinterface.scs_workspace.models import TavernaExecution
from masterinterface.scs_workspace.forms import TavernaExecutionForm
from masterinterface.scs.utils import get_file_data
from raven.contrib.django.raven_compat.models import client
from piston.utils import rc
# import the logging library
import logging

import redis
import pickle
import hashlib as hl
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

EMPTY_BACLAVA = '<?xml version="1.0" encoding="UTF-8"?><b:dataThingMap xmlns:b="http://org.embl.ebi.escience/baclava/0.1alpha"></b:dataThingMap>'

gc_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
class workflows_api(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def create(self, request, *args, **kwargs):
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if request.method == 'POST':
                optionals = ['tags','semanticAnnotations','localID', 'resourceURL']
                post  = request.POST.copy()
                for option in optionals:
                    if post.get(option, None) is None:
                        post[option] = ''
                #post['global_id'] = post['globalID']
                form = WorkflowForm(post, request.FILES)
                if form.is_valid():
                    workflow = form.save(owner=user)
                    return workflow.global_id
                logger.error('API:Update workflow bad request', exc_info=True, extra={
                    'request': request,
                    'form': form.errors
                    })
            return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR

    def update(self, request, global_id=None, *args, **kwargs):
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if global_id:
                dbWorkflow = Workflow.objects.get(global_id=global_id)
            else:
                return rc.BAD_REQUEST
            if not dbWorkflow.resource_ptr.can_edit(user):
                response = HttpResponse(status=403)
                response._is_string = True
                return response

            if request.method == 'PUT':
                put = request.PUT.copy()
                for key in dbWorkflow.metadata:
                    if request.PUT.get(key,None) is None or  request.PUT.get(key,None) == "":
                        if key not in ['linkedTo'] and dbWorkflow.metadata[key] == None:
                            put[key] = ''
                        else:
                            put[key] = dbWorkflow.metadata[key]
                form = WorkflowForm(put, request.FILES, instance=dbWorkflow)
                if form.is_valid():
                    workflow = form.save(commit=False, owner=dbWorkflow.owner)
                    #fix to the taverna online update injection.
                    workflow.xml = dbWorkflow.xml
                    workflow.save()
                    return workflow.global_id
                #logger.error('API:Update workflow bad request', exc_info=True, extra={
                #    'request': request,
                #    'form': form.errors,
                #    'put' : put
                #    })
            return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR

    def delete(self, request, global_id=None, *args, **kwargs):
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if global_id:
                dbWorkflow = Workflow.objects.get(global_id=global_id)
            else:
                return rc.BAD_REQUEST
            if not dbWorkflow.resource_ptr.can_edit(user):
                return rc.FORBIDDEN
            if request.method == 'DELETE':
                dbWorkflow.delete()
                return rc.DELETED
            return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR

    def read(self, request, global_id=None):
        """
            Process a search user request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            global_id (list): list of global id to check
            ticket (string) : the authentication ticket - optional

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN

            if global_id:
                try:
                    workflow = Workflow.objects.get(global_id=global_id)
                except:
                    return rc.NOT_FOUND
                if user is not None and workflow.resource_ptr.can_read(user):
                    t2flow = inputDefinition = ''
                    if workflow.t2flow:
                        t2flow = workflow.t2flow.read()
                    if workflow.xml:
                        inputDefinition = workflow.xml.read()
                    return {'global_id': workflow.global_id,
                            't2flow': base64.b64encode(t2flow),
                            'input_definition': base64.b64encode(inputDefinition),
                            'metadata': workflow.metadata}
                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response
            else:
                workflows = Workflow.objects.filter_by_roles(role="Reader", user=user, types='Workflow', numResults=300)
                results = []
                for workflow in workflows['data']:
                    t2flow = inputDefinition = ''
                    if workflow.t2flow:
                        t2flow = workflow.t2flow.read()
                    if workflow.xml:
                        inputDefinition = workflow.xml.read()
                    results.append({'global_id': workflow.global_id,
                                    't2flow': base64.b64encode(t2flow),
                                    'input_definition': base64.b64encode(inputDefinition),
                                    'metadata': workflow.metadata}
                    )
                return results
        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            client.captureException()
            return response

class WfMngApiHandler(BaseHandler):
    """
    REST service based on Django-Piston Library
    """

    def create(self, request, *args, **kwargs):
        """
        Submits the workflow with the `global_id` specified in the request, and starts its execution.

        Parameters:
         - `request`: request
         - `args`: args
         - `kwargs`: kwargs
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if request.method == 'POST':
                global_id = request.POST.get('global_id', None)
                if global_id and Workflow.objects.filter(global_id=global_id).count() == 0:
                    return rc.NOT_FOUND

                input = request.POST.get('input', None)
                workflow = Workflow.objects.get(global_id=global_id)
                form = TavernaExecutionForm()
                taverna_execution = form.save(commit=False)
                n = TavernaExecution.objects.filter(title__contains=workflow.metadata['name'], ticket=ticket).count() + 1
                title = workflow.metadata['name'] + " execution " + str(n)
                taverna_execution.title = title
                taverna_execution.t2flow = get_file_data(workflow.t2flow)
                if input!=None:
                   taverna_execution.baclava = base64.b64decode(input)
                else:
                   taverna_execution.baclava = get_file_data(workflow.xml)
                taverna_execution.owner = user

                taverna_execution.status = 'Ready to run'
                taverna_execution.executionstatus = 0
                ## only for test mode
                taverna_execution.url = ''
                taverna_execution.taverna_atomic_id = 404
                ####
                taverna_execution.save()

                if taverna_execution.t2flow!= "" and taverna_execution.baclava!= "":
                    taverna_execution.start(user.userprofile.get_ticket(7))
                    #return eid
                    return taverna_execution.id
                return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR


    def read(self,  request, wfrun_id=None,  *args, **kwargs):
        """
        Get the information about the workflow run specified in the request.

        Parameters:
         - `request`: request
         - `wfrun_id`: workflow run id
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    pass #return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if wfrun_id:
                taverna_execution = TavernaExecution.objects.get(pk=wfrun_id, ticket=ticket)
                keys = ['executionstatus', 'error', 'error_msg', 'workflowId', 'endpoint', 'asConfigId', 'expiry', 'startTime', 'Finished', 'exitcode', 'stdout', 'stderr', 'outputfolder', 'is_running', 'output']
                results = {}
                for key in keys:
                    results[key] = getattr(taverna_execution, key)
                return results
            return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR


    def delete(self, request, wfrun_id=None,  *args, **kwargs):
        """
        Deletes the workflow run specified in the request

        Parameters:
         - `request`: request
         - `wfrun_id`: workflow run id
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    pass #return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if wfrun_id is not None:
                taverna_execution = TavernaExecution.objects.get(pk=wfrun_id, ticket=ticket)
                if taverna_execution.delete(ticket = ticket):
                    return True
            return rc.BAD_REQUEST
        except Exception, e:
            client.captureException()
            return rc.INTERNAL_ERROR

class GCMngApiHandler(BaseHandler):
    """
    REST service based on Django-Piston Library
    """
    allowed_methods = ('GET','PUT','DELETE')

    def read(self, request, cache_namespace=None, cache_key=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            r = _get_rcache()
            key = _get_hash_key(cache_namespace, cache_key)
            if r and key:
                data = r.get(key)
                if data is not None:
                    return pickle.loads(data)
                else:
                    return rc.NOT_FOUND
            else:
                return rc.NOT_FOUND
        else:
            return rc.FORBIDDEN

    def update(self, request, cache_namespace=None, cache_key=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)
        ttl = _check_header_ttl(request)

        if ticket is not None:
            r = _get_rcache()
            key = _get_hash_key(cache_namespace, cache_key)

            if r and key:
                tmp = r.get(key)
                tmp = pickle.loads(tmp) if tmp is not None else None

                if tmp is not None and tmp['meta']['owner'] != ticket[1].username:
                    return rc.FORBIDDEN

                data = { 'meta': { 'owner': ticket[1].username }}
                try:
                    data['data'] = json.loads(str(request.body))
                    r.setex(key,pickle.dumps(data),ttl)

                except Exception, e:
                    data['error'] = { 'type': 'error', 'msg': str(e) }

                return data
            else:
                return rc.NOT_FOUND

        else:
            return rc.FORBIDDEN

    def delete(self, request, cache_namespace=None, cache_key=None,  *args, **kwargs):
        ticket = _check_header_ticket(request)

        if ticket is not None:
            r = _get_rcache()
            key = _get_hash_key(cache_namespace, cache_key)

            if r and key:
                tmp = r.get(key)
                tmp = pickle.loads(tmp) if tmp is not None else None

                if tmp is not None and tmp['meta']['owner'] != ticket[1].username:
                    return rc.FORBIDDEN

                r.delete(key)
                return rc.DELETED
            else:
                return rc.NOT_FOUND
        else:
            return rc.FORBIDDEN

def _check_header_ticket(req):
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

def _check_header_ttl(req):
    """GC_TTL: in seconds, defaults to 86400secs - 1d"""
    return req.META.get('HTTP_GC_TTL', '86400')

def _get_rcache(pool=gc_pool):
    """returns selected cache."""
    cc = redis.Redis(connection_pool=pool)
    return cc

def _get_hash_key(data, *args):
    """get sha1 sum hexdigest for a string"""
    return hl.sha1( ":".join([data] + [el for el in args]) ).hexdigest()
