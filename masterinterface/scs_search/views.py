"""
    scs_search: views.py Module
"""
__author__ = ''

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from urllib import quote
from connector import automatic_search_connector
from connector import guided_search_s1_connector
from connector import guided_search_s2_connector
from connector import complex_query_connector


def automatic_search_view( request ):
    """
        Automatic Search view
    """

    return render_to_response( 'scs_search/scs_search.html', None,
                              RequestContext( request ) )


def guided_search_view( request) :
    """
        Guided Search view
    """

    return render_to_response( 'scs_search/scs_search.html', None,
                              RequestContext( request ) )


@csrf_exempt
def automatic_search_service( request ):
    """
        Automatic Search Service
    """

    if request.method == 'POST':

        free_text = request.POST[ 'input' ]
        connector = automatic_search_connector( quote( free_text ) )

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

    terms = ''

    if request.method == 'POST':

        groups_query = request.POST[ 'groups_query' ]
        load_groups = simplejson.loads( groups_query )

        for ( j, group ) in enumerate( load_groups ):
            if j == 0:
                if len( group ) > 1:
                    for ( i, concept ) in enumerate( group ):
                        if i < len( group ) - 1:
                            terms = terms + ' ( ' + concept + ' OR '
                        else:
                            terms = terms + concept + ' ) '
                else:
                    terms = terms + ' ( ' + group[0] + ' ) '
            else:
                if len( group ) > 1:
                    for ( i, concept ) in enumerate( group ):
                        if i < len(group) - 1:
                            terms = terms + 'AND ( ' + concept + ' OR '
                        else:
                            terms = terms + concept + ' ) '
                else:
                    terms = terms + 'AND ( ' + group[0] + ' ) '

        connector = complex_query_connector( quote( terms ) )

        response = HttpResponse( content = connector,
                                content_type = 'application/json ')
        response._is_string = False

        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response



def search_permalink( request ):

    if request.method == 'GET':

        return HttpResponse( status = 200 );

    return HttpResponse( status = 403 )
