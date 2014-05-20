"""
    scs_search: views.py Module
"""
__author__ = ''

from urllib import quote, unquote
from datetime import datetime
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

from masterinterface.atos.semantic_connector import *
from models import Query
from json2sparql import json2sparql


def automatic_search_view( request ):
    """
        Automatic Search view
    """
    breadcrum = [0, 0, 0]
    if request.GET.get('input', None) is not None:
        results = automatic_search_connector(quote(request.GET['input']), request.user)
        breadcrum[0] = 1
    else:
        results = ''

    return render_to_response('scs_search/scs_search.html',
                              {'search': 'automatic', 'results': results, 'dataset': '', 'class': '',
                               'breadcrum': breadcrum, 'classLabel': ''},
                              RequestContext(request))


def advance_search_view(request):
    dataset = ''
    datasetLabel = ''
    conceptClass = ''
    user = request.user
    name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")
    results = ''
    breadcrum = [0, 0, 0]
    if request.GET.get('groups_query', None) is not None:

        groups_query = unquote(request.GET['groups_query'])
        load_groups = simplejson.loads(groups_query)

        ####### Save History #######
        if user.is_authenticated():
            query_obj = Query(name=name, query=groups_query)
            query_obj.save()
            query_obj.user.add(user)

        results = complex_query_connector(load_groups, request.user)
        breadcrum[0] = 1
    elif request.GET.get('id', None) is not None:

        query_obj = Query.objects.get(id=request.GET['id'])
        groups_query = unquote(query_obj.query)
        load_groups = simplejson.loads(groups_query)

        ####### Save History #######
        query_obj = Query.objects.get(id=id)
        if user.is_authenticated():
            if not query_obj.saved:
                query_obj.name = name
            query_obj.query = groups_query
            query_obj.date = datetime.utcnow()
            query_obj.save()
            query_obj.user.add(user)

        results = complex_query_connector(load_groups, request.user)
        breadcrum[0] = 1

    return render_to_response('scs_search/scs_search.html',
                              {'search': 'complex', 'results': results, 'dataset': dataset, 'datasetLabel': datasetLabel
                                  , 'class': conceptClass, 'breadcrum': breadcrum, 'classLabel': ''},
                              RequestContext(request))


def class_search_view(request):
    """
        Guided Search view
    """
    dataset = ''
    datasetLabel = ''

    if request.GET.get('dataset', None) is not None:

        dataset = unquote(request.GET['dataset'])
        datasetLabel = unquote(request.GET['datasetLabel'])
        allConcepts = class_search_connector(None, datasetLabel, num_max_hits='200', page_num='1').get('1',[])
    else:

        return HttpResponseRedirect(reverse('automaticSearch'))

    return render_to_response('scs_search/scs_search.html',
                              {'search': 'guided', 'results': allConcepts, 'dataset': dataset, 'datasetLabel': datasetLabel,
                               'class': '', 'breadcrum': [1, 1, 0], 'classLabel': ''},
                              RequestContext(request))

def class_search_view_service(request):
    """
        Guided Search view
    """
    dataset = ''
    datasetLabel = ''

    if request.GET.get('dataset', None) is not None:

        dataset = unquote(request.GET['dataset'])
        datasetLabel = unquote(request.GET['datasetLabel'])
        allConcepts = class_search_connector(None, datasetLabel, num_max_hits='200', page_num='1').get('1',[])

        return HttpResponse(content=json.dumps(allConcepts), content_type='application/json')


def annotation_search_view(request):
    """
        annotation Search view
    """
    dataset = ''
    datasetLabel = ''
    conceptClass = ''
    conceptLabel = ''
    user = request.user
    name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")
    results = ''
    explore = ''
    if request.GET.get('groups_query', None) is not None:

        groups_query = unquote(request.GET['groups_query'])
        load_groups = simplejson.loads(groups_query)
        dataset = unquote(request.GET['dataset'])
        datasetLabel = unquote(request.GET['datasetLabel'])
        conceptClass = class_search_connector(None, datasetLabel, num_max_hits='200', page_num='1').get('1',[])

        import re
        r = re.compile('sparqlEndpoint=(.*?)&')
        endpoint_url = r.search(dataset)
        ####### Save History #######
        query_obj = Query(name=name, query=groups_query)
        query_obj.save()
        query_obj.user.add(user)
        query_sparql = json2sparql(load_groups)
        results =dataset_query_connector(query_sparql, endpoint_url, request.user.username, request.COOKIES.get('vph-tkt', ''))
    elif request.GET.get('id', None) is not None:

        query_obj = Query.objects.get(id=request.GET['id'])
        groups_query = unquote(query_obj.query)
        load_groups = simplejson.loads(groups_query)

        ####### Save History #######
        query_obj = Query.objects.get(id=id)
        if not query_obj.saved:
            query_obj.name = name
        query_obj.query = groups_query
        query_obj.date = datetime.utcnow()
        query_obj.save()
        query_obj.user.add(user)

        results = complex_query_connector(load_groups, request.user)
    if request.GET.get('dataset', None) is not None:
        dataset = unquote(request.GET['dataset'])
        datasetLabel = unquote(request.GET['datasetLabel'])
        import re
        r = re.compile('sparqlEndpoint=(.*?)&')
        endpoint_url = r.search(dataset)
        if 'read/sparql' in endpoint_url.group(1):
            explore = endpoint_url.group(1).replace('read/sparql', 'explore/sql.html')
        conceptClass = class_search_connector(None, datasetLabel, num_max_hits='200', page_num='1').get('1',[])
        #conceptClass = unquote(request.GET['conceptClass'])
        #conceptClassLabel = unquote(request.GET['conceptLabel'])
        #annotations = annotation_search_connector(None, dataset, conceptClass, conceptClassLabel, num_max_hits='200', page_num='1')

    return render_to_response('scs_search/scs_search.html',
                              {'search': 'complex', 'results': results, 'dataset': dataset, 'datasetLabel': datasetLabel
                                  , 'class': conceptClass, 'breadcrum': [1, 1, 1], 'classLabel': conceptLabel, 'conceptClass': conceptClass, 'explore':explore},
                              RequestContext(request))

def annotation_search_view_results(request):
    """
        annotation Search view
    """
    dataset = ''
    datasetLabel = ''
    conceptClass = ''
    conceptLabel = ''
    explore = ''
    user = request.user
    name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")
    results = ''
    if request.GET.get('groups_query', None) is not None:

        groups_query = unquote(request.GET['groups_query'])
        load_groups = simplejson.loads(groups_query)
        dataset = unquote(request.GET['dataset'])
        datasetLabel = unquote(request.GET['datasetLabel'])
        conceptClass = class_search_connector(None, datasetLabel, num_max_hits='200', page_num='1').get('1',[])

        import re
        r = re.compile('sparqlEndpoint=(.*?)&')
        endpoint_url = r.search(dataset)
        if 'read/sparql' in endpoint_url.group(1):
            explore = endpoint_url.group(1).replace('read/sparql', 'explore/sql.html')
        ####### Save History #######
        if request.user.is_authenticated():
            query_obj = Query(name=name, query=groups_query)
            query_obj.save()
            query_obj.user.add(user)

        query_sparql = json2sparql(load_groups)
        results =dataset_query_connector(query_sparql, endpoint_url, request.user.username, request.COOKIES.get('vph-tkt', ''))

    return render_to_response('scs_search/scs_search.html',
                              {'search': 'complex', 'queryresults': results, 'dataset': dataset, 'datasetLabel': datasetLabel
                                  , 'class': conceptClass, 'breadcrum': [1, 1, 1], 'load_groups': json.dumps(groups_query) , 'conceptClass':conceptClass, 'explore':explore},
                              RequestContext(request))


@csrf_exempt
def automatic_search_service( request ):
    """
        Automatic Search Service
    """

    if request.method == 'POST':
        free_text = request.POST['input']
        connector = json.dumps(automatic_search_connector(quote(free_text), request.user), sort_keys=False)

        response = HttpResponse(content=connector,
                                content_type='application/json')
        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def guided_search_s1_service(request):
    """
        Guided Search Step1 Service
    """

    if request.method == 'POST':
        free_text = request.POST['input']
        num_max_hits = request.POST['nummaxhits']
        page_num = request.POST['pagenum']

        connector = guided_search_s1_connector(quote(free_text),
                                               num_max_hits, page_num)

        response = HttpResponse(content=connector,
                                content_type='application/json')

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def guided_search_s2_service( request ):
    """
        Guided Search Step2 Service
    """

    if request.method == 'POST':
        concept_uri_list = request.POST['concept_uri_list']
        connector = guided_search_s2_connector(quote(concept_uri_list))

        response = HttpResponse(content=connector,
                                content_type='application/json')
        response._is_string = False

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def complex_query_service(request):
    """
        Complex Query Service
    """

    if request.method == 'POST':

        groups_query = request.POST['groups_query']
        id = request.POST.get('id', "")
        load_groups = simplejson.loads(groups_query)

        ####### Save History #######
        user = request.user
        name = 'query-' + datetime.utcnow().strftime("%Y-%m-%d-%H:%M")

        try:
            if id == "":
                query_obj = Query(name=name, query=groups_query)
            else:
                query_obj = Query.objects.get(id=id)
                if not query_obj.saved:
                    query_obj.name = name
                query_obj.query = groups_query
                query_obj.date = datetime.utcnow()
            if user.is_authenticated():
                query_obj.save()
                query_obj.user.add(user)
        except Exception, e:
            pass
            ############################

        connector = json.dumps(complex_query_connector(load_groups,request.user), sort_keys=False)

        response = HttpResponse(content=connector,
                                content_type='application/json ')
        response._is_string = False

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def save_complex_query( request ):
    """
    """

    if request.method == 'POST':

        query = request.POST['groups_query']
        name = request.POST['name']
        id = request.POST['id']
        user = request.user

        try:
            if id != '':

                query_obj = Query.objects.get(id=id)
                query_obj.name = name
                query_obj.query = query
                query_obj.saved = True

            else:
                query_obj = Query(name=name, query=query, saved=True)

            query_obj.save()
            query_obj.user.add(user)

            response = HttpResponse(status=200, content_type='application/json ')
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
            latest_query = Query.objects.filter(user=user).order_by('-date')
            latest_query_dict = []
            for query in latest_query[:5]:
                latest_query_dict.append([query.id, query.name, query.query])
            for query in latest_query[5:]:
                if query.saved:
                    latest_query_dict.append([query.id, query.name, query.query])

            response = HttpResponse(content=json.dumps(latest_query_dict), content_type='application/json ')

            response._is_string = False

            return response

        except Exception, e:
            return


@csrf_exempt
def class_search_service(request):
    """
        Guided Search Step1 Service
    """

    if request.method == 'POST':
        free_text = request.POST['input']
        num_max_hits = request.POST['nummaxhits']
        page_num = request.POST['pagenum']
        dataset = request.POST['dataset']

        connector = class_search_connector(quote(free_text), dataset, num_max_hits, page_num)

        response = HttpResponse(content=connector, content_type='application/json')

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def annotation_search_service(request):
    """
        Guided Search Step1 Service
    """

    if request.method == 'POST':
        free_text = request.POST.get('input', None)
        num_max_hits = request.POST['nummaxhits']
        page_num = request.POST['pagenum']
        dataset = request.POST['dataset']
        classConcept = request.POST['classConcept']
        classLabel = request.POST['classLabel']

        connector = annotation_search_connector(free_text, dataset, classConcept, classLabel, num_max_hits, page_num, )

        response = HttpResponse(content=connector, content_type='application/json')

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


@csrf_exempt
def dataset_query_service( request ):
    """
        Complex Query Service
    """

    if request.method == 'POST':
        query_request = simplejson.loads(request.POST['groups_query'])
        id = request.POST.get('id', "")
        endpoint = request.POST.get('endpoint', "")

        query_sparql = json2sparql(query_request)

        import re

        r = re.compile('sparqlEndpoint=(.*?)&')
        endpoint_url = r.search(endpoint)
        from masterinterface.atos.exceptions import AtosPermissionException
        try:
            connector = json.dumps(dataset_query_connector(query_sparql, endpoint_url, request.user.username, request.COOKIES.get('vph-tkt', '')), sort_keys=False)
        except AtosPermissionException, e:
            response = HttpResponse(status=401)
            response._is_string = False
            return response


        response = HttpResponse(content=connector,
                                content_type='application/json ')
        response._is_string = False

        return response

    response = HttpResponse(status=403)
    response._is_string = True

    return response


def search_permalink(request):
    """
    """

    if request.method == 'GET':
        return HttpResponse(status=200)

    return HttpResponse(status=403)
