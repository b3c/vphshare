__author__ = ""
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
#from piston.handler import BaseHandler
from urllib import quote
from connector import automaticSearchConnector
from connector import guidedSearchS1Connector
from connector import guidedSearchS2Connector
from connector import guidedSearchComplexQueryConnector


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


@csrf_exempt
def guidedSearchComplexQueryService( request ):
    """
    """

    terms = ""

    if request.method == "POST":

        groups_query = request.POST['groups_query']
        load_groups = simplejson.loads( groups_query )

        for j, group in enumerate(load_groups):

            if j == 0:
                if len(group) > 1:
                    for i, concept in enumerate(group):
                        if i < len(group) - 1:
                            terms = terms + '(' + concept + ' OR '
                        else:
                            terms = terms + concept + ')'
                else:
                    terms = terms + '(' + group[0] + ')'
            else:
                if len(group) > 1:
                    for i, concept in enumerate(group):
                        if i < len(group) - 1:
                            terms = terms + ' AND (' + concept + ' OR '
                        else:
                            terms = terms + concept + ')'
                else:
                    terms = terms + ' AND (' + group[0] + ')'

        connector = guidedSearchComplexQueryConnector( quote( terms ) )

        response = HttpResponse(content=connector, content_type="application/json")
        response._is_string = False

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response