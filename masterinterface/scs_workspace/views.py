from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from core import WorkflowManager
from exceptions import WorkflowManagerException
from models import TavernaExecution
from masterinterface.scs_resources.models import Workflow


def workspace(request):

    executions = TavernaExecution.objects.filter(owner=request.user)
    return render_to_response(
        'scs_workspace/workspace.html',
        {'executions': executions},
        RequestContext(request)
    )


def submit(request):
    pass


def start(request, id='1'):
    pass