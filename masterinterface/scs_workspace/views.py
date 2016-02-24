from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from models import TavernaExecution
from forms import TavernaExecutionForm
from masterinterface.scs.utils import get_file_data
from masterinterface.scs_resources.models import Workflow, Resource
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from masterinterface.scs_workspace.Taverna2WorkflowIO import Taverna2WorkflowIO
from masterinterface.datasets.models import DatasetQuery
from raven.contrib.django.raven_compat.models import client

_CUSTOM_HEADERS = ["CustomValueFromInput", "WorkflowOutFolderPath"]


@login_required
def workspace(request):
    executions = TavernaExecution.objects.filter(
        owner=request.user,
        ticket=request.ticket).order_by('-creation_datetime')

    return render_to_response(
        'scs_workspace/workspace.html',
        {'executions': executions},
        RequestContext(request)
    )


@login_required
def create(request):
    if request.method == 'POST' and request.POST.get('workflowId', None):
        form = TavernaExecutionForm()
        workflow = Workflow.objects.get(global_id=request.POST['workflowId'])
        taverna_execution = form.save(commit=False)
        taverna_execution.title = request.POST['title']
        taverna_execution.t2flow = get_file_data(workflow.t2flow)

        if request.POST.get('default_inputs', 'off') == 'on':
            if request.POST['input_definition_tab'] == 'baclava':

                # get file from post request
                taverna_execution.baclava = get_file_data(
                    request.FILES['inputFile']).replace('\r', '')

                # if filename is a csv file we convert to baclava
                fname = request.FILES['inputFile'].name
                if (fname.lower().endswith(".csv")):
                    try:
                        tavernaIO = Taverna2WorkflowIO()
                        tavernaIO.loadInputsFromCSVString(
                            taverna_execution.baclava)

                        # the xml baclava file
                        taverna_execution.baclava = tavernaIO.inputsToBaclava()

                    # fail to load from csv
                    except Exception:
                        client.captureException()

            if request.POST['input_definition_tab'] == 'dataset':
                dataset_query = DatasetQuery.objects.get(
                    id=request.POST['dataset_queryid'])
                tavernaIO = Taverna2WorkflowIO()
                tavernaIO.loadFromT2FLOWString(taverna_execution.t2flow)
                tavernaIO.loadInputsFromCSVFile

                input_ports = tavernaIO.getInputPorts()
                results = dataset_query.get_results(request.ticket)
                header = dataset_query.get_header(request.ticket)

                idx = 1
                for input in input_ports:
                    dataset_results_field = request.POST[input]
                    values = []

                    if dataset_results_field in _CUSTOM_HEADERS:
                        tmpInput = "CustomInput-%d" % (idx,)

                        custom_value = str( request.POST[tmpInput] )
                        custom_vector = [ custom_value for _ in range(len(results)) ]

                        values.extend(custom_vector)
                    else:
                        index = header.index(dataset_results_field)
                        for row in results:
                            values.append(row[index])

                    tavernaIO.setInputPortValues(input, values)
                    idx += 1

                taverna_execution.baclava = tavernaIO.inputsToBaclava()
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
        tavernaIO = Taverna2WorkflowIO()
        dataset_queries = request.user.datasetquery_set.all().values('id','name')
        return render_to_response(
        'scs_workspace/create.html',
        {'form': form, 'workflow': workflow, 'dataset_queries':dataset_queries},
        RequestContext(request)
        )
    else:
        raise PermissionDenied

@csrf_exempt
def getDatasetInputs(request):
    value = request.POST['value']
    dataset_query = DatasetQuery.objects.get(id=value)
    dataset = Resource.objects.get(global_id=dataset_query.global_id)
    (rel_guids, rel_datasets) = dataset_query.send_data_intersect_summary_with_metadata(request.ticket)

    workflow = Workflow.objects.get(global_id=request.POST['workflowId'])
    tavernaIO = Taverna2WorkflowIO()
    tavernaIO.loadFromT2FLOWString(workflow.t2flow)
    #tavernaIO.loadInputsFromBaclavaString(workflow.xml)
    workflow_input = tavernaIO.getInputPorts()

    query_headers = dataset_query.get_header(request.ticket)
    query_headers.extend(_CUSTOM_HEADERS)

    return render_to_response(
        'scs_workspace/datasetInputs.html',
        {'workflow_input': workflow_input, \
            'dataset': dataset, \
            'rel_datasets': rel_datasets , \
            'dataset_query':dataset_query, \
            'query_header': query_headers,\
            'results':dataset_query.get_results(request.ticket)},
        RequestContext(request)
    )



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
