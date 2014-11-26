# Create your views here.
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.shortcuts import render_to_response
from django.core.exceptions import SuspiciousOperation
from django.template import RequestContext
from django.http import Http404, HttpResponseNotAllowed, HttpResponseBadRequest


def query_builder(request):
    """Home view """

    if request.user.is_authenticated():
        print ""

    return render_to_response(
        'datasets/query_builder.html',
        {},
        RequestContext(request)
    )
