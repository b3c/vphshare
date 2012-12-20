"""
    scs_search: views.py Module
"""
__author__ = ''

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from urllib import quote, unquote
from connector import automatic_search_connector
from connector import guided_search_s1_connector
from connector import guided_search_s2_connector
from connector import complex_query_connector
from models import Query
import json


def automatic_search_view( request ):
    """
        Automatic Search view
    """
    if request.GET.get('input',None) is not None:
        results = automatic_search_connector( quote( request.GET['input'] ) )
    else:
        results = ""

    return render_to_response( 'scs_search/scs_search.html', {'search':'automatic','results':results},
                              RequestContext( request ) )


def complex_search_view( request) :
    """
        Guided Search view
    """

    if request.GET.get('groups_query',None) is not None:

        groups_query = unquote(request.GET[ 'groups_query' ])
        load_groups = simplejson.loads( groups_query )

        results = complex_query_connector( load_groups )
    else:
        results = ""

    return render_to_response( 'scs_search/scs_search.html', {'search':'complex', 'results':results},
                              RequestContext( request ) )

def guided_search_view( request) :
    """
        Guided Search view
    """

    return render_to_response( 'scs_search/scs_search.html', {'search':'guided'},
        RequestContext( request ) )


@csrf_exempt
def automatic_search_service( request ):
    """
        Automatic Search Service
    """

    if request.method == 'POST':

        free_text = request.POST[ 'input' ]
        connector = json.dumps(automatic_search_connector( quote( free_text ) ), sort_keys = False )

        response = HttpResponse( content = connector,
                                content_type = 'application/json' )
        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response


@csrf_exempt
def guided_search_s1_service(request):
    """
        Guided Search Step1 Service
    """

    if request.method == 'POST':

        free_text = request.POST[ 'input' ]
        num_max_hits = request.POST[ 'nummaxhits' ]
        page_num = request.POST[ 'pagenum' ]

        connector = guided_search_s1_connector( quote( free_text ),
                num_max_hits, page_num )

        response = HttpResponse( content = connector,
                                content_type = 'application/json' )

        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response


@csrf_exempt
def guided_search_s2_service( request ):
    """
        Guided Search Step2 Service
    """

    if request.method == 'POST':

        concept_uri_list = request.POST[ 'concept_uri_list' ]
        connector = guided_search_s2_connector( quote( concept_uri_list ) )

        response = HttpResponse( content = connector,
                                content_type = 'application/json' )
        response._is_string = False

        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response


@csrf_exempt
def complex_query_service( request ):
    """
        Complex Query Service
    """

    if request.method == 'POST':

        groups_query = request.POST[ 'groups_query' ]
        load_groups = simplejson.loads( groups_query )

        # Save History
        #save_complex_query( request )

        connector = json.dumps( complex_query_connector( load_groups ), sort_keys = False )

        response = HttpResponse( content = connector,
                                content_type = 'application/json ')
        response._is_string = False

        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response


@csrf_exempt
def save_complex_query( request ):
    """
    """

    if request.method == 'POST':

        query = request.POST[ 'groups_query' ]
        name = request.POST[ 'name' ]
        user = request.user

        try:
            query_obj = Query( name=name, query=query )
            query_obj.save()
            query_obj.user.add( user )
            
            response = HttpResponse(status=200, content_type = 'application/json ')
            response._is_string = False

            return response

        except Exception, e:
            return


def get_latest_query( request ):
    """
    """

    if request.method == 'POST':

        user = request.user

        try:
            latest_query = Query.objects.filter( user = user ).order_by('date')[:5]

            return latest_query

        except Exception, e:
            return


def search_permalink( request ):
    """
    """

    if request.method == 'GET':

        return HttpResponse( status = 200 );

    return HttpResponse( status = 403 )
