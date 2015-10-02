__author__ = 'm.balasso@scsitaly.com, a.saglimbeni@scsitaly.com'

import re

import requests
import xmltodict
from ordereddict import OrderedDict
from raven.contrib.django.raven_compat.models import client
from jsonpath_rw import parse
from masterinterface.atos.config import *
from exceptions import AtosServiceException

JSON_XPATH_PARSER  = parse('resource_metadata[*].gm.*')

def decompose_payload(sub_metadata):

    s = "<%s>%s</%s>"
    results = ""
    for key, item in sub_metadata.items():
        content = ""
        if isinstance(item, list):
            for i in item:
                content += decompose_payload(i)
        elif isinstance(item, dict):
            content = decompose_payload(item)
        else:
            content = item
        results += s %(key,content,key)
    return results


def from_dict_to_payload(metadata,type):
    typetag= type[0].lower()+ type[1:]
    return "<resource_metadata><%s>%s</%s></resource_metadata>" % (typetag, decompose_payload(metadata), typetag)


def set_resource_metadata(metadata, type):
    """
        given a metadata dictionary create a new entry into the global catalog.
        return the resource global id as a string
    """

    try:
        headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
        response = requests.post(GLOBAL_METADATA_API, data=from_dict_to_payload(metadata, type), headers=headers)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        regEx = re.compile('global_id>(.*?)<')

        return regEx.search(response.text).group(1)

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)

def update_resource_metadata(global_id, metadata, type):
    """
        given a metadata dictionary and a resource global id, update the resource medatada into the global catalog.
        return the resource global id as a string
    """

    try:
        headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
        response = requests.put(RESOURCE_METADATA_API % global_id, data=from_dict_to_payload(metadata, type), headers=headers)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        regEx = re.compile('global_id>(.*?)<')

        return regEx.search(response.text).group(1)

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)

def delete_resource_metadata(global_id):
    """
        given a metadata dictionary and a resource global id, update the resource medatada into the global catalog.
        return the resource global id as a string
    """

    try:
        headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
        response = requests.delete(RESOURCE_METADATA_API % global_id, headers=headers)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        return True

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def get_resource_metadata(global_id):
    """
        given a resource global id return its metadata as a dictionary
    """
    try:
        response = requests.get(RESOURCE_METADATA_API % global_id, headers={'Content-Type':'application/xml', 'Accept' : 'application/json'})

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        single_resource = parse('gm.*')
        response = single_resource.find(response.json())[0].value
        return response
    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)

def get_resources_metadata_by_list(global_id = [], page=1, numResults=10, orderBy = 'name', orderType='asc', search_text = '' ,filters = {}):
    """
        given the list of the resource given a list of global_id
    """
    try:
        filters_url = "((status='Active') OR (status='active')) AND "
        for key, values in filters.items():
            if type(values) is list and len(values) > 0:
                filters_url += '('
                for value in values:
                    if key == 'tags':
                        filters_url += " %s LIKE '%%25%s%%25' OR" % (key, value)
                    else:
                        filters_url += " %s='%s' OR" % (key, value)
                filters_url = filters_url[:-2]
                filters_url += ") AND "
        filters_url = filters_url[:-5]
        if list(global_id) == []:
            return EMPTY_LIST.copy()
        payload = decompose_payload({'globalID_list':",".join(global_id)})
        response = requests.post(FILTER_METADATA_BY_GLOBALID % ( search_text, filters_url, numResults, page, orderBy, orderType), headers={'Content-Type':'application/xml', 'Accept' : 'application/json'}, data=payload)
        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        try:
            response = response.json()
            resources = JSON_XPATH_PARSER.find(response)
            pages = response["numTotalMetadata"] / numResults
            if response["numTotalMetadata"] % numResults != 0:
                pages += 1
            response['resource_metadata'] = resources
            response['pages'] = pages
            return response
        except Exception, e:
            client.captureException()
            return EMPTY_LIST.copy()
    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)

def filter_resources_by_facet(type, facet = None, value = None, page=1, numResults=10, orderBy = 'name', orderType='asc'):
    """
        given a facet and a value return the list of the resources that match the query
    """

    try:
        if facet:
            response = requests.get(FACETS_METADATA_API % (type, facet, value,numResults, page, orderBy, orderType), headers={'Accept' : 'application/json'})
        else:
            response = requests.get(TYPE_METADATA_API % (type, numResults, page, orderBy, orderType), headers={'Accept' : 'application/json'})

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        try:
            response = response.json()
            resources = JSON_XPATH_PARSER.find(response)
            pages = response["numTotalMetadata"] / numResults
            if response["numTotalMetadata"] % numResults != 0:
                pages += 1
            response['resource_metadata'] = resources
            response['pages'] = pages
            return response
        except Exception, e:
            client.captureException()
            return EMPTY_LIST.copy()

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)

def search_resource(text, filters = {}, numResults=10, page=1, orderBy = 'name', orderType='asc', global_id = []):

    try:
        if text == '*':
            filters_url = "(name LIKE '%%25') AND ((status='Active') OR (status='active')) AND "
            for key, values in filters.items():
                if type(values) is list and len(values) > 0:
                    filters_url += '('
                    for value in values:
                        if key == 'tags':
                            filters_url += " %s LIKE '%%25%s%%25' OR" % (key, value)
                        else:
                            filters_url += " %s='%s' OR" % (key, value)
                    filters_url = filters_url[:-2]
                    filters_url += ") AND "
            filters_url = filters_url[:-5]
            if list(global_id) == []:
                response = requests.get(FILTER_METADATA_API % (filters_url, numResults, page, orderBy, orderType), headers={'Accept' : 'application/json'})
            else:
                payload = decompose_payload({'globalID_list':",".join(global_id)})
                response = requests.post(FILTER_METADATA_API % (filters_url, numResults, page, orderBy, orderType), headers={'Content-Type':'application/xml', 'Accept' : 'application/json'}, data=payload)
        else:
            request_url = SEARCH_METADATA_API % (text, numResults, page, orderBy, orderType)
            #filters['name'] = text.split()
            filters_url = "&filters=((status='Active') OR (status='active')) AND "
            for key, values in filters.items():
                if type(values) is list and len(values) > 0:
                    filters_url += '('
                    for value in values:
                        if key == 'tags':
                            filters_url += " %s LIKE '%%s%' OR" % (key, value)
                        else:
                            filters_url += " %s='%s' OR" % (key, value)
                    filters_url = filters_url[:-2]
                    filters_url += ') AND '
            filters_url = filters_url[:-5]
            if list(global_id) == []:
                response = requests.get(request_url + filters_url, headers={'Accept' : 'application/json'})
            else:
                payload = decompose_payload({'globalID_list':",".join(global_id)})
                response = requests.post(request_url + filters_url, headers={'Content-Type':'application/xml', 'Accept' : 'application/json'}, data=payload)


        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        response = response.json()
        resources = JSON_XPATH_PARSER.find(response)
        pages = response["numTotalMetadata"] / numResults
        if response["numTotalMetadata"] % numResults != 0:
            pages += 1
        response['resource_metadata'] = resources
        response['pages'] = pages
        return response

    except Exception, e:
        return EMPTY_LIST.copy()
