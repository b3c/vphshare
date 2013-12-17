import os
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from core import WorkflowManager
from exceptions import WorkflowManagerException
from models import TavernaExecution
from forms import TavernaExecutionForm
from masterinterface.scs.utils import get_file_data
from masterinterface.scs_resources.models import Workflow
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json


def workspace(request):

    executions = TavernaExecution.objects.filter(owner=request.user)

    return render_to_response(
        'scs_workspace/workspace.html',
        {'executions': executions},
        RequestContext(request)
    )


def create(request):
    if request.method == 'POST' and request.POST.get('workflowId',None):
        form = TavernaExecutionForm()
        workflow = Workflow.objects.get(global_id=request.POST['workflowId'])
        taverna_execution = form.save(commit=False)
        taverna_execution .title = request.POST['title']
        taverna_execution.t2flow = get_file_data(workflow.t2flow)
        if request.POST.get('default_inputs','off') == 'on':
            taverna_execution.baclava = get_file_data(request.FILES['inputFile'])
        else:
            taverna_execution.baclava = get_file_data(workflow.xml)
        #taverna_execution.baclava = get_file_data(workflow.xml)
        taverna_execution.owner = request.user
        taverna_execution.status = 'Created'
        ## only for test mode
        taverna_execution.url = request.POST['taverna_url']
        taverna_execution.taverna_atomic_id = request.POST['taverna_servers']
        ####
        taverna_execution.save()
        request.session['statusmessage'] = "The workflow execution has been correctly created"
        return redirect('workspace')
    if request.method == 'GET' and request.GET.get('workflow_id',None):
        workflow = Workflow.objects.get(pk=request.GET['workflow_id'])
        n = TavernaExecution.objects.filter(title__contains=workflow.metadata['name']).count() + 1
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
def changeStatus(request):

    try:
        if request.method == 'POST' and request.POST.get('eid', None):
            user = User.objects.get(username= request.POST['user'])
            taverna_execution = TavernaExecution.objects.get(pk=int(request.POST['eid']), owner=user)
            taverna_execution.status = request.POST['status']
            if taverna_execution.status == "Error on submiting":
                taverna_execution.as_config_id = ''
                taverna_execution.url = ''
                taverna_execution.taverna_id = ''
            taverna_execution.save()
            taverna_execution.save()
            return HttpResponse(status=200)
    except Exception, e:
        pass

    return HttpResponse(status=403)

@csrf_exempt
def startExecution(request):

    try:
        if request.method == 'POST' and request.POST.get('eid', None):
            taverna_execution = TavernaExecution.objects.get(pk=request.POST['eid'], owner=request.user)
            ret = WorkflowManager.execute_workflow( request.COOKIES.get('vph-tkt'), taverna_execution.id, taverna_execution.title, taverna_execution.taverna_atomic_id, taverna_execution.t2flow, taverna_execution.baclava, taverna_execution.url)
            taverna_execution.status = 'Executing'
            taverna_execution.save()
            return HttpResponse(content=json.dumps(ret))
    except Exception, e:
        pass

    return HttpResponse(status=403)


@csrf_exempt
def deleteExecution(request):
    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        ret = WorkflowManager.deleteExecution(taverna_execution.id,  request.COOKIES.get('vph-tkt'))
        if ret == 'True':
            taverna_execution.delete()
            return HttpResponse(content=json.dumps({'results': 'true'}))
    return HttpResponse(status=403)


@csrf_exempt
def getExecutionInfo(request):
    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        ret = WorkflowManager.getWorkflowInformation(taverna_execution.id, request.COOKIES.get('vph-tkt'))
        if ret != False:
            results = [ret.get('executionstatus', ''), ret.get('error', ''), ret.get('error_msg', '') , ret.get('workflowId', ''), ret.get('endpoint', ''), ret.get('asConfigId', ''), ret.get('createTime',''), ret.get('expiry',''), ret.get("startTime",''), ret.get('Finished',''), ret.get('exitcode',''),ret.get('stdout',''), ret.get('stderr',''), ret.get('outputfolder', '')]
        else:
            results = [0, False, '' , '', taverna_execution.url, '', '', '', '', '', '','', '', '']
        return HttpResponse(content=json.dumps(results))

    return HttpResponse(status=403)
