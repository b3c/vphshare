__author__ = 'Alfredo Saglimbeni'
import base64
from django.db.models import Q
from permissions.models import PrincipalRoleRelation
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs_resources.forms import WorkflowForm
from masterinterface.scs_resources.models import Workflow
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
                optionals = ['tags','semantic_annotations']
                for option in optionals:
                    if request.POST.get(option, None) is None:
                        request.POST[option] = ''
                form = WorkflowForm(request.POST, request.FILES)
                if form.is_valid():
                    workflow = form.save(owner=user)
                    return workflow.global_id
            return rc.BAD_REQUEST
        except Exception, e:
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
            if dbWorkflow.owner != user:
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
            if dbWorkflow.owner != user:
                return rc.FORBIDDEN
            if request.method == 'DELETE':
                dbWorkflow.delete()
                return rc.DELETED
            return rc.BAD_REQUEST
        except Exception, e:
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
                if user is not None and PrincipalRoleRelation.objects.filter( Q(user=user) | Q(group__in=user.groups.all()), content_id=workflow.resource_ptr.id ).count() > 0:
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
                workflows = Workflow.objects.all()
                results = []
                for workflow in workflows:
                    if user is not None and PrincipalRoleRelation.objects.filter( Q(user=user) | Q(group__in=user.groups.all()), content_id=workflow.resource_ptr.id ).count() > 0:
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
            return response
