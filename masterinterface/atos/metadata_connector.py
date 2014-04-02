__author__ = 'm.balasso@scsitaly.com, a.saglimbeni@scsitaly.com'


import re
import requests
import xmltodict
from masterinterface.atos.config import *
from exceptions import AtosServiceException
from ordereddict import OrderedDict

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
    typefield = "<type>%s</type>" % type
    #"".join(["<%s>%s</%s>" % (key, item, key) for key, item in metadata.items()]
    return "<resource_metadata><%s>%s%s</%s></resource_metadata>" % (typetag, typefield, decompose_payload(metadata), typetag)


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


def get_resource_metadata(global_id):
    """
        given a resource global id return its metadata as a dictionary
    """
    try:
        response = requests.get(RESOURCE_METADATA_API % global_id)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        metadata = xmltodict.parse(response.text.encode('utf-8'))
        result = metadata['resource_metadata']
        return result[result.keys()[0]]

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


def get_facets():
    """
        return the facets list
    """

    return FACETS_LIST


def filter_resources_by_facet(type, facet = None, value = None):
    """
        given a facet and a value return the list of the resources that match the query
    """

    try:
        if facet:
            response = requests.get(FACETS_METADATA_API % (type, facet, value))
        else:
            response = requests.get(TYPE_METADATA_API % type)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        try:
            resources = xmltodict.parse(response.text.encode('utf-8'))["resource_metadata_list"]['resource_metadata']
            results = []
            if not isinstance(resources, list):
                resources = [resources]
            for resource in resources:
                resource = resource[resource.keys()[0]]
                results.append(resource)
            return results
        except Exception, e:
            return []

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def filter_resources_by_author(author):
    """
    """
    try:
        query = "(author='%s')" % author
        response = requests.get(FILTER_METADATA_API % (query, '3000', '1'))

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)
        try:
            resources = xmltodict.parse(response.text.encode('utf-8'))["resource_metadata_list"]['resource_metadata']
            results = []
            if not isinstance(resources, list):
                resources = [resources]
            for resource in resources:
                resource = resource[resource.keys()[0]]
                results.append(resource)
            return results
        except Exception, e:
            return []

    except BaseException, e:
        raise AtosServiceException("Error while contacting Atos Service: %s" % e.message)


def filter_resources_by_type(resource_type):
    """
    """

    return filter_resources_by_facet(resource_type)

#not used?
def filter_resources_by_text(text):
    """
    """

    resources = get_all_resources_metadata()

    for resource in resources:
        if not str(resource.items()).count(text):
            resources.remove(resource['resource_metadata'])

    return resources

logicalExpressionBase = '(name:"%s" OR description:"%s")'

#not used?
def filter_resources_by_expression(expression):
    """

    """
    logicalExpression = logicalExpressionBase % (expression['search_text'], expression['search_text'])
    for key, values in expression.items():
        if type(values) is list and len(values) > 0:
            logicalExpression += '('
            for value in values:
                logicalExpression += ' %s="%s" OR' % (key, value)
            logicalExpression = logicalExpression[:-2]
            logicalExpression += ') AND '

    try:
        response = requests.get(FILTER_METADATA_API % logicalExpression)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        #from ordereddict import OrderedDict
        resources = xmltodict.parse(response.text.encode('utf-8'))["resource_metadata_list"]["resource_metadata"]
        if not isinstance(resources, list):
            resources = [resources]
        results = OrderedDict()
        for resource in resources:
            position = str(resource.values()).count(expression['search_text'])

            if position not in results:
                results[position] = []
            results[position].append(resource)

        keys = results.keys()
        keys.sort(reverse=True)
        resources = []
        countType = {}
        for key in keys:
            for resource in results[key]:
                if resource['type'] not in countType:
                    countType[resource['type']] = 0
                countType[resource['type']] += 1
                resources.append(resource)

        return resources, countType

    except BaseException, e:
        return [],{}


def search_resource(text, filters = {}, numResults=10, page=1):

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
            response = requests.get(FILTER_METADATA_API % (filters_url, numResults, page))
        else:
            request_url = SEARCH_METADATA_API % (text, numResults, page)
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

            response = requests.get(request_url + filters_url)

        if response.status_code != 200:
            raise AtosServiceException("Error while contacting Atos Service: status code = %s" % response.status_code)

        #from collections import OrderedDict
        respDict = xmltodict.parse(response.text.encode('utf-8'))
        pages = (int(respDict["resource_metadata_list"]['@numTotalMetadata'])/numResults) + 1
        resources = respDict["resource_metadata_list"]["resource_metadata"]
        countType = {'Dataset': 0, 'Workflow': 0, 'AtomicService': 0, 'File': 0, 'SemanticWebService': 0, 'Workspace': 0}
        if not isinstance(resources, list):
            resources = [resources]

        results = []
        for resource in resources:
            resource = resource[resource.keys()[0]]
            results.append(resource)
            countType[resource['type']] += 1
        return results, countType, pages
    except BaseException, e:
        print e
        return [], {}, 0
