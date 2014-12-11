import os
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from models import TavernaExecution
from forms import TavernaExecutionForm
from masterinterface.scs.utils import get_file_data
from masterinterface.scs_resources.models import Workflow
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json


@login_required
def workspace(request):

    executions = TavernaExecution.objects.filter(owner=request.user, ticket=request.ticket).order_by('-creation_datetime')

    return render_to_response(
        'scs_workspace/workspace.html',
        {'executions': executions},
        RequestContext(request)
    )

@login_required
def create(request):
    if request.method == 'POST' and request.POST.get('workflowId',None):
        form = TavernaExecutionForm()
        workflow = Workflow.objects.get(global_id=request.POST['workflowId'])
        taverna_execution = form.save(commit=False)
        taverna_execution.title = request.POST['title']
        taverna_execution.t2flow = get_file_data(workflow.t2flow)
        if request.POST.get('default_inputs','off') == 'on':
            taverna_execution.baclava = get_file_data(request.FILES['inputFile'])
        else:
            taverna_execution.baclava = get_file_data(workflow.xml)
        #taverna_execution.baclava = get_file_data(workflow.xml)
        taverna_execution.owner = request.user
        taverna_execution.status = 'Ready to run'
        taverna_execution.executionstatus = 0
        ## only for test mode
        taverna_execution.url = request.POST['taverna_url']
        taverna_execution.taverna_atomic_id = request.POST['taverna_servers']
        ####
        taverna_execution.save()
        request.session['statusmessage'] = "The workflow execution has been correctly created"
        return redirect('workspace')
    if request.method == 'GET' and request.GET.get('workflow_id',None):
        workflow = Workflow.objects.get(pk=request.GET['workflow_id'])
        n = TavernaExecution.objects.filter(title__contains=workflow.metadata['name'], ticket=request.ticket).count() + 1
        form = TavernaExecutionForm()
        form.fields['workflowId'].initial = workflow.global_id
        form.fields['title'].initial = workflow.metadata['name'] + " execution " + str(n)
        return render_to_response(
        'scs_workspace/create.html',
        {'form': form, 'workflow': workflow},
        RequestContext(request)
        )
    else:
        raise PermissionDenied

@csrf_exempt
def startExecution(request):
    try:
        if request.method == 'POST' and request.POST.get('eid', None):
            taverna_execution = TavernaExecution.objects.get(pk=request.POST['eid'], ticket=request.ticket , owner=request.user)
            taverna_execution.start(request.user.userprofile.get_ticket(7))
            return HttpResponse(content=json.dumps(True))
    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        pass
    return HttpResponse(status=403)


@csrf_exempt
def deleteExecution(request):
    if request.method == 'POST' and request.POST.get('eid', None):
        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'), ticket=request.ticket)
        if taverna_execution.delete(ticket = request.ticket):
            return HttpResponse(content=json.dumps({'results': 'true'}))
    return HttpResponse(status=403)


@csrf_exempt
def getExecutionInfo(request):
    if request.method == 'POST' and request.POST.get('eid', None):
        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'), ticket=request.ticket)
        keys = ['executionstatus', 'error', 'error_msg', 'workflowId', 'endpoint', 'asConfigId', 'expiry', 'startTime', 'Finished', 'exitcode', 'stdout', 'stderr', 'outputfolder', 'output', 'is_running']
        results = []
        for key in keys:
            results.append(getattr(taverna_execution, key))
        return HttpResponse(content=json.dumps(results))
    return HttpResponse(status=403)
