# Create your views here.
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.shortcuts import render_to_response
from django.core.exceptions import SuspiciousOperation
from django.template import RequestContext
from django.http import Http404, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse
import json

from masterinterface.scs_resources.models import Resource
from masterinterface.scs.views import page403


def query_builder(request, global_id):
    """Home view """

    if request.user.is_authenticated():
        dataset = Resource.objects.get(global_id=global_id)
        dataset.load_additional_metadata(request.ticket)
        return render_to_response(
            'datasets/query_builder.html',
            {'dataset': dataset},
            RequestContext(request)
        )
    return page403(request)


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