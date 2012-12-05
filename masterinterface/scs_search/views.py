__author__ = ""
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
#from piston.handler import BaseHandler
from urllib import quote
from connector import automaticSearchConnector
from connector import guidedSearchS1Connector
from connector import guidedSearchS2Connector


def automaticSearchView( request ):
    """
        automaticSearch view
    """

    return render_to_response("scs_search/scs_search.html",
        None,
        RequestContext(request))


def guidedSearchView( request ):
    """
        guidedSearch view
    """

    return render_to_response("scs_search/scs_search.html",
        None,
        RequestContext(request))


@csrf_exempt
def automaticSearchService( request ):
    """
    """
    if request.method == "POST":

        free_text = request.POST['input']
        connector = automaticSearchConnector( quote( free_text ) )

        response = HttpResponse(content=connector, content_type="application/json")
        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def guidedSearchS1Service( request ):
    """
    """
    if request.method == "POST":

        free_text = request.POST['input']
        connector = guidedSearchS1Connector( quote( free_text ) )

        response = HttpResponse(content=connector, content_type="application/json")

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def guidedSearchS2Service( request ):
    """
    """
    if request.method == "POST":

        concept_uri_list = request.POST['concept_uri_list']
        connector = guidedSearchS2Connector( quote( concept_uri_list ) )

        response = HttpResponse(content=connector, content_type="application/json")
        response._is_string = False

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response