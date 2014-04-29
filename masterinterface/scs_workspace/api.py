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
                optionals = ['tags','semanticAnnotations']
                for option in optionals:
                    if request.POST.get(option, None) is None:
                        request.POST[option] = ''
                form = WorkflowForm(request.POST, request.FILES)
                if form.is_valid():
                    workflow = form.save(owner=user)
                    return workflow.global_id
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
                for key in dbWorkflow.metadata:
                    if request.PUT.get(key,None) is None:
                        request.PUT[key] = dbWorkflow.metadata[key]
                form = WorkflowForm(request.PUT, request.FILES, instance=dbWorkflow)
                if form.is_valid():
                    workflow = form.save(commit=False, owner=dbWorkflow.owner)
                    workflow.save()
                    return rc.CREATED
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
                workflows = Workflow.objects.all(metadata=True)
                results = []
                for workflow in workflows:
                    if user is not None and workflow.resource_ptr.can_read(user):
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

                workflow = Workflow.objects.get(global_id=global_id)
                form = TavernaExecutionForm()
                taverna_execution = form.save(commit=False)
                n = TavernaExecution.objects.filter(title__contains=workflow.metadata['name'], ticket=ticket).count() + 1
                title = workflow.metadata['name'] + " execution " + str(n)
                taverna_execution.title = title
                taverna_execution.t2flow = get_file_data(workflow.t2flow)
                taverna_execution.baclava = get_file_data(workflow.xml)
                taverna_execution.owner = user

                taverna_execution.status = 'Ready to run'
                taverna_execution.executionstatus = 0
                ## only for test mode
                taverna_execution.url = ''
                taverna_execution.taverna_atomic_id = 245
                ####
                taverna_execution.save()

                if taverna_execution.t2flow!= "" and taverna_execution.baclava!= "":
                    taverna_execution.start(ticket)
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
                keys = ['executionstatus', 'error', 'error_msg', 'workflowId', 'endpoint', 'asConfigId', 'expiry', 'startTime', 'Finished', 'exitcode', 'stdout', 'stderr', 'outputfolder', 'is_running']
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
