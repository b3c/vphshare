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
from datetime import datetime
from connector import automatic_search_connector, guided_search_s1_connector , guided_search_s2_connector, complex_query_connector, annotation_search_connector
from models import Query
import json


def automatic_search_view( request ):
    """
        Automatic Search view
    """
    if request.GET.get('input',None) is not None:
        results = automatic_search_connector( quote( request.GET['input'] ) )
    else:
        results = ''

    return render_to_response( 'scs_search/scs_search.html', {'search':'automatic','results':results, 'dataset': ''},
                              RequestContext( request ) )


def complex_search_view( request) :
    """
        Guided Search view
    """
    dataset = ''
    datasetLabel = ''
    user = request.user
    name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")
    results = ''
    if request.GET.get('groups_query',None) is not None:

        groups_query = unquote(request.GET[ 'groups_query' ])
        load_groups = simplejson.loads( groups_query )

        ####### Save History #######
        query_obj = Query( name=name, query=groups_query )
        query_obj.save()
        query_obj.user.add( user )

        results = complex_query_connector( load_groups )
    elif request.GET.get('id',None) is not None:

        query_obj = Query.objects.get( id = request.GET[ 'id' ] )
        groups_query = unquote(query_obj.query)
        load_groups = simplejson.loads( groups_query )

        ####### Save History #######
        query_obj = Query.objects.get(id=id)
        if not query_obj.saved:
            query_obj.name = name
        query_obj.query = groups_query
        query_obj.date = datetime.utcnow()
        query_obj.save()
        query_obj.user.add( user )


        results = complex_query_connector( load_groups )
    elif request.GET.get('dataset',None) is not None:
        dataset = unquote(request.GET[ 'dataset' ])
        datasetLabel = unquote(request.GET[ 'datasetLabel' ])

    return render_to_response( 'scs_search/scs_search.html', {'search':'complex', 'results':results, 'dataset' : dataset, 'datasetLabel' : datasetLabel, },
                              RequestContext( request ) )

def guided_search_view( request) :
    """
        Guided Search view
    """

    return render_to_response( 'scs_search/scs_search.html', {'search':'guided', 'results': '', 'dataset': ''},
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
        id = request.POST.get('id',"")
        load_groups = simplejson.loads( groups_query )

        ####### Save History #######
        user = request.user
        name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")

        try:
            if id == "" :
                query_obj = Query( name=name, query=groups_query )
            else:
                query_obj = Query.objects.get(id=id)
                if not query_obj.saved:
                    query_obj.name = name
                query_obj.query = groups_query
                query_obj.date = datetime.utcnow()
            query_obj.save()
            query_obj.user.add( user )
        except Exception, e:
            return
        ############################

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
        id = request.POST[ 'id' ]
        user = request.user

        try:
            if id != '':

                query_obj = Query.objects.get(id=id)
                query_obj.name = name
                query_obj.query = query
                query_obj.saved = True

            else:
                query_obj = Query( name=name, query=query , saved = True )


            query_obj.save()
            query_obj.user.add( user )

            
            response = HttpResponse(status=200, content_type = 'application/json ')
            response._is_string = False

            return response

        except Exception, e:
            return

@csrf_exempt
def get_latest_query( request ):
    """
    """

    if request.method == 'POST':

        user = request.user

        try:
            latest_query = Query.objects.filter( user = user  ).order_by( '-date' )
            latest_query_dict = []
            for query in latest_query[:5]:
                latest_query_dict.append( [ query.id, query.name, query.query ] )
            for query in latest_query[5:]:
                if query.saved:
                    latest_query_dict.append( [ query.id, query.name, query.query ] )

            response = HttpResponse( content = json.dumps(latest_query_dict), content_type = 'application/json ')

            response._is_string = False

            return response

        except Exception, e:
            return


@csrf_exempt
def annotation_search_service(request):
    """
        Guided Search Step1 Service
    """

    if request.method == 'POST':

        free_text = request.POST[ 'input' ]
        num_max_hits = request.POST[ 'nummaxhits' ]
        page_num = request.POST[ 'pagenum' ]

        connector = annotation_search_connector( quote( free_text ),
            num_max_hits, page_num )

        response = HttpResponse( content = connector,
            content_type = 'application/json' )

        return response

    response = HttpResponse( status = 403 )
    response._is_string = True

    return response

def search_permalink( request ):
    """
    """

    if request.method == 'GET':

        return HttpResponse( status = 200 )

    return HttpResponse( status = 403 )
