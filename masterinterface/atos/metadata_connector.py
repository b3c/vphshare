__author__ = 'm.balasso@scsitaly.com, a.saglimbeni@scsitaly.com'


import re
import requests
import xmltodict
from masterinterface.atos.config import *
from exceptions import AtosServiceException


def from_dict_to_payload(metadata):

    return "<metadata>%s</metadata>" % "".join(["<%s>%s</%s>" % (key, item, key) for key, item in metadata.items()])


def get_all_resources_metadata():
    """
        return a list of dict with all the resources found into the global catalog
    """
    try:
        response = requests.get(GLOBAL_METADATA_API)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        metadata = xmltodict.parse(response.text.encode('utf-8'))

        return metadata["resource_metadata_list"]["resource_metadata"]

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def set_resource_metadata(metadata):
    """
        given a metadata dictionary create a new entry into the global catalog.
        return the resource global id as a string
    """

    try:
        headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
        response = requests.post(GLOBAL_METADATA_API, data=from_dict_to_payload(metadata), headers=headers)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        regEx = re.compile('global_id>(.*?)<')

        return regEx.search(response.text).group(1)

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def get_resource_metadata(global_id):
    """
        given a resource global id return its metadata as a dictionary
    """
    try:
        response = requests.get(RESOURCE_METADATA_API % global_id)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        metadata = xmltodict.parse(response.text.encode())

        return metadata['resource_metadata']

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def update_resource_metadata(global_id, metadata):
    """
        given a metadata dictionary and a resource global id, update the resource medatada into the global catalog.
        return the resource global id as a string
    """

    try:
        headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
        response = requests.put(RESOURCE_METADATA_API % global_id, data=from_dict_to_payload(metadata), headers=headers)

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


def get_facets():
    """
        return the facets list
    """

    return FACETS_LIST


def filter_resources_by_facet(facet, value):
    """
        given a facet and a value return the list of the resources that match the query
    """

    try:
        response = requests.get(FACETS_METADATA_API % (facet, value))

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        metadata = xmltodict.parse(response.text.encode())

        return metadata["resource_metadata_list"]['resource_metadata']

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def filter_resources_by_author(author):
    """
    """

    return filter_resources_by_facet('author', author)


def filter_resources_by_type(resource_type):
    """
    """

    return filter_resources_by_facet('type', resource_type)


def filter_resources_by_facets(query):
    """
        given a dictionary query, a list of resources that match all the given condition is returned
    """

    if not type(query) is dict:
        raise TypeError("A dictionary type is required for query parameter")

    resources = filter_resources_by_facet(query.keys()[0], query[query.keys()[0]])

    del query[query.keys()[0]]

    for facet, value in query.items():
        for resource in resources:
            if not facet in resource or not resource[facet].count(value):
                resources.remove(resource)

    return resources


def filter_resources_by_text(text):
    """
    """

    resources = get_all_resources_metadata()

    for resource in resources:
        if not str(resource.items()).count(text):
            resources.remove(resource['resource_metadata'])

    return resources


def filter_resources_by_expression(expression):
    """

    """

    return []