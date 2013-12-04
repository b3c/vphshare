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
def startTaverna(request):

    try:
        if request.method == 'POST' and request.POST.get('eid', None):
            taverna_execution = TavernaExecution.objects.get(pk=request.POST['eid'], owner=request.user)
            taverna_execution.status = 'Starting Taverna Server'
            taverna_execution.save()
            ret = WorkflowManager.createTavernaServerWorkflow(request.user.username, request.COOKIES.get('vph-tkt'))
            taverna_execution.status = "Inizialized"
            taverna_execution.as_config_id = ret['asConfigId']
            taverna_execution.url = ret['tavernaURL']
            taverna_execution.taverna_id = ret['tavernawfId']
            taverna_execution.save()
            ret['results'] = 'true'
            return HttpResponse(content=json.dumps(ret))
    except Exception, e:
        pass

    return HttpResponse(status=403)


@csrf_exempt
def submitWorkflow(request):

    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        taverna_execution.status = 'Submiting Workflow to Taverna'
        taverna_execution.save()
        ret = WorkflowManager.submitWorkflow(
            taverna_execution.title,
            taverna_execution.t2flow,
            taverna_execution.baclava,
            request.COOKIES.get('vph-tkt')
        )

        if 'workflowId' in ret and ret['workflowId']:
            taverna_execution.workflowId = ret['workflowId']
            taverna_execution.status = 'Workflow ready to run'
            taverna_execution.save()
            return HttpResponse(content=json.dumps({'results': 'true'}))
        else:
            taverna_execution.status = 'Error during Workflow submition'
            return HttpResponse(content=json.dumps({'results': 'false','errorcode':ret.get('error.code', '500'),'errordescription':ret.get('error.code', '500')}))

    return HttpResponse(status=403)


@csrf_exempt
def startWorkflow(request):

    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        taverna_execution.status = 'Starting Workflow'
        taverna_execution.save()

        ret = WorkflowManager.startWorkflow(taverna_execution.workflowId, request.COOKIES.get('vph-tkt'))
        if 'workflowId' in ret and ret['workflowId']:
            taverna_execution.workflowId = ret['workflowId']
            taverna_execution.status = 'Workflow Running'
            taverna_execution.save()
            return HttpResponse(content=json.dumps({'results': 'true'}))
        else:
            taverna_execution.status = 'Error during workflow starting'
            return HttpResponse(content=json.dumps({'results': 'false', 'errorcode': ret.get('error.code', '500'),
                                         'errordescription': ret.get('error.code', '500')}))

    return HttpResponse(status=403)


@csrf_exempt
def deleteWorkflow(request):
    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        taverna_execution.status = 'Deleting Workflow'
        taverna_execution.save()
        try:
            ret = WorkflowManager.deleteWorkflow(taverna_execution.workflowId, request.COOKIES.get('vph-tkt'))
        except Exception, e:
            pass
        ret = WorkflowManager.deleteTavernaServerWorkflow(taverna_execution.taverna_id, request.user.username, request.COOKIES.get('vph-tkt'))
        if 'workflowId' in ret and ret['workflowId']:

            taverna_execution.status = 'Workflow Deleted'
            taverna_execution.save()

            taverna_execution.delete()

            return HttpResponse(content=json.dumps({'results': 'true'}))
        else:
            return HttpResponse(content=json.dumps({'results': 'false', 'errorcode': ret.get('error.code', '500'),
                                         'errordescription': ret.get('error.code', '500')}))

    return HttpResponse(status=403)


@csrf_exempt
def getExecutionInfo(request):
    if request.method == 'POST' and request.POST.get('eid', None):

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        if taverna_execution.workflowId != '':
            ret = WorkflowManager.getWorkflowInformation(taverna_execution.workflowId, request.COOKIES.get('vph-tkt'))
            if 'workflowId' in ret and ret['workflowId']:

                if ret['status'] == 'Finished':
                    taverna_execution.status = ret['status']
                taverna_execution.save()

                results = [ taverna_execution.status, taverna_execution.taverna_id, taverna_execution.url,
                  taverna_execution.as_config_id, taverna_execution.workflowId, ret.get('createTime',''), ret.get('expiry',''),
                  ret.get("startTime",''), ret.get('Finished',''), ret.get('complete',''), ret.get('exitcode',''),
                  ret.get('stdout',''), ret.get('stderr','')]

                return HttpResponse(content=json.dumps(results))
            else:
                return HttpResponse(content=json.dumps({'results': 'false', 'errorcode': ret.get('error.code', '500'),
                                             'errordescription': ret.get('error.code', '500')}))
        else:
            ret = {}
            results = [ taverna_execution.status, taverna_execution.taverna_id, taverna_execution.url,
                  taverna_execution.as_config_id, taverna_execution.workflowId, ret.get('createTime',''), ret.get('expiry',''),
                  ret.get("startTime",''), ret.get('Finished',''), ret.get('complete',''), ret.get('exitcode',''),
                  ret.get('stdout',''), ret.get('stderr','')]
            return HttpResponse(content=json.dumps(results))

    return HttpResponse(status=403)
