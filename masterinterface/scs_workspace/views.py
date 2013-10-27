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


def workspace(request):

    executions = TavernaExecution.objects.filter(owner=request.user)
    running_tavernas = []
    try:
        ret = WorkflowManager.getTavernaServersList(request.COOKIES.get('vph-tkt'))
        running_tavernas = ret.get('servers', [])
    except WorkflowManagerException, e:
        request.session['errormessage'] = "Error %s : %s" % (e.code, e.description)
        running_tavernas = []
    return render_to_response(
        'scs_workspace/workspace.html',
        {'executions': executions,
         'tavernas': running_tavernas},
        RequestContext(request)
    )


def create(request):

    if request.method == 'POST':
        form = TavernaExecutionForm(request.POST)
        if form.is_valid():
            workflow = Workflow.objects.get(pk=form.data['workflow_id'])
            taverna_execution = form.save(commit=False)
            taverna_execution.t2flow = get_file_data(workflow.t2flow)
            if form.data['default_inputs']:
                taverna_execution.baclava = get_file_data(workflow.xml)
            taverna_execution.owner = request.user
            taverna_execution.status = 'Created'
            taverna_execution.save()

            request.session['statusmessage'] = "The workflow execution has been correctly created"

            return workspace(request)


        else:
            return render_to_response(
                'scs_workspace/create.html',
                {'workflow': Workflow.objects.get(pk=form.data['workflow_id']),
                 'form': form,
                 'inputs': []},
                RequestContext(request)
            )


def submit(request):

    if request.method == 'POST':

        certificate_file = "vph.cyfronet.crt"
        plugin_properties_file = "vphshare.properties"

        #HACK we have a lazy programmer here!
        abs_path = os.path.abspath(os.path.dirname(__file__))
        plugin_definition = open(os.path.join(abs_path, 'plugins.xml'), 'r').read()

        taverna_execution = TavernaExecution.objects.get(pk=request.POST.get('eid'))
        ret = WorkflowManager.submitWorkflow(
            taverna_execution.title,
            taverna_execution.t2flow,
            taverna_execution.baclava,
            plugin_definition,
            certificate_file,
            plugin_properties_file,
            request.COOKIES.get('vph-tkt')
        )

        if 'workflowId' in ret and ret['workflowId']:
            taverna_execution.workflowId = ret['workflowId']
            taverna_execution.status = 'Initialized'
            request.session['statusmessage'] = 'The worfklow execution has been correctly submitted'
        else:
            request.session['errormessage'] = "Error %s : %s" % (ret.get('error.code', '500'), ret.get('error.description', 'Ouch!'))

    return workspace(request)


def starttaverna(request):
    if request.method == 'POST':
        WorkflowManager.createTavernaServerWorkflow('51ded4da86648825040093fe', request.user.username, request.COOKIES.get('vph-tkt'))
        request.session['statusmessage'] = 'Taverna server created'

    return workspace(request)

def start(request, id='1'):
    pass