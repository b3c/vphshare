# Create your views here.
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.shortcuts import render_to_response
from django.core.exceptions import SuspiciousOperation
from django.template import RequestContext
from django.http import Http404, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from masterinterface.scs_resources.models import Resource
from masterinterface.scs.views import page403
from masterinterface.datasets.models import DatasetQuery

@login_required
def query_builder(request, global_id):
    """Home view """

    if request.user.is_authenticated():
        dataset = Resource.objects.get(global_id=global_id)
        if not dataset.can_read(request.user):
            return page403(request)
        query_to_load = None
        if "q" in request.GET:
            try:
                dataset_query = DatasetQuery.objects.get(id=request.GET['q'])
                query_to_load= {
                    "id" : dataset_query.id,
                    "name": dataset_query.name,
                    "query": json.loads(dataset_query.query)
                }
            except Exception, e:
                request.session['errormessage'] = "The query you are looking for doesn't exist."
                redirect("query_builder",global_id=global_id)
        dataset.load_additional_metadata(request.ticket)
        endpoint = dataset.metadata.get('sparqlEndpoint',dataset.metadata['localID'])
        if 'read/sparql' not in endpoint:
            request.session['errormessage'] = "The dataset you are looking for is not supported with the new query builder. Please update and try again."
            endpoint = 'False'
        else:
            endpoint = 'True'
        return render_to_response(
            'datasets/query_builder.html',
            {'dataset': dataset , "query_to_load": query_to_load, "query_list":request.user.datasetquery_set.filter(global_id=global_id), "endpoint":endpoint},
            RequestContext(request)
        )
    return page403(request)

@login_required
def get_dataset_schema(request):
    if request.method == 'GET' and 'global_id' in request.GET:
        global_id = request.GET['global_id']
        dataset = Resource.objects.get(global_id=global_id)
        dataset.load_additional_metadata(request.ticket)
    else:
        return page403(request)
    return HttpResponse(status=200,
                        content=json.dumps(dataset.metadata['schema'], sort_keys=False),
                        content_type='application/json')
@login_required
@csrf_exempt
def get_results(request):
    if request.user.is_authenticated() and request.method == 'POST' and 'globalID' in request.POST:
        global_id = request.POST['globalID']
        json_query = request.POST['query']
        dataset = Resource.objects.get(global_id=global_id)
        dataset.load_additional_metadata(request.ticket)
        dataset_query = DatasetQuery(query=json_query, global_id=global_id)
        dataset_query.save()
        dataset_query.user.add(request.user)
        header = dataset_query.get_header(request.ticket)
        results = dataset_query.get_results(request.ticket)
        dataset_query.delete()
        return HttpResponse(status=200,
                        content=json.dumps(
                            {
                                "header": header,
                                "results": results
                            }, sort_keys=False),
                        content_type='application/json')
    else:
        return page403(request)

@login_required
@csrf_exempt
def save_the_query(request):
    if request.user.is_authenticated() and request.method == 'POST' and 'globalID' in request.POST:
        global_id = request.POST['globalID']
        json_query = request.POST['query']
        name = request.POST['name']
        dataset_query = DatasetQuery(name=name, query=json_query, global_id=global_id)
        dataset_query.save()
        dataset_query.user.add(request.user)
        dataset_query.save()
        return HttpResponse(status=200,
                        content=json.dumps(
                            {
                                "saved": True,
                                "id": dataset_query.id
                            }, sort_keys=False),
                        content_type='application/json')
    else:
        return page403(request)

@login_required
@csrf_exempt
def edit_the_query(request):
    if request.user.is_authenticated() and request.method == 'POST' and 'globalID' in request.POST:
        global_id = request.POST['globalID']
        json_query = request.POST['query']
        name = request.POST['name']
        query_id = request.POST['q']
        dataset_query = DatasetQuery.objects.get(id=query_id)
        dataset_query.name = name
        dataset_query.query = json_query
        dataset_query.global_id = global_id
        dataset_query.save()
        if request.user.username not in dataset_query.user.all().values_list('username', flat=True):
            dataset_query.user.add(request.user)
        dataset_query.save()
        return HttpResponse(status=200,
                        content=json.dumps(
                            {
                                "saved": True,
                                "id": dataset_query.id
                            }, sort_keys=False),
                        content_type='application/json')
    else:
        return page403(request)

@login_required
@csrf_exempt
def delete_the_query(request):
    if request.user.is_authenticated() and request.method == 'POST' and 'globalID' in request.POST:
        query_id = request.POST['q']
        dataset_query = DatasetQuery.objects.get(id=query_id)
        dataset_query.delete()
        return HttpResponse(status=200,
                        content=json.dumps(
                            {
                                "deleted": True
                            }, sort_keys=False),
                        content_type='application/json')
    else:
        return page403(request)