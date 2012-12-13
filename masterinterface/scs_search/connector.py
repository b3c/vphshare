__author__ = ""

import requests
import json
from config import *
from lxml import etree
from ordereddict import OrderedDict

def automaticSearchConnector( free_text ):
    """
        automaticSearchConnector: Call the automaticSearch API
        and extract the result from XML.

        Arguments:
            freeText (string): input text

        Returns:
            dataset (list): list of dataset grouped by concept_uri

    """
    results = OrderedDict()

    response = requests.get( AUTOMATIC_SEARCH_API % free_text )

    doc = etree.fromstring( response.text.encode() )

    concept_list = doc

    for concept_elem in concept_list:
        dataset = OrderedDict()
        concept_uri = concept_elem.attrib['uri']

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib[ 'label' ]
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset[dataset_label] = [ num_metch, rdf_data ]

        results[concept_uri] = dataset

    json_results = json.dumps( results, sort_keys=False )

    return json_results


def guidedSearchS1Connector( free_text, nummaxhits , pagenum ):
    """
        guidedSearchS1Connector: Call the guidedSearchS1 API
        and extract the result from XML.

        Arguments:
            freeText (string): input text

        Returns:
            dataset (list): list of concept/terms
    """
    results = OrderedDict()

    response = requests.get( GUIDED_SEARCH_S1_API % (free_text, nummaxhits, PAGE_SIZE, pagenum) )
    doc = etree.fromstring( response.text.encode() )

    root_elem = doc

    results['max_matches'] =  root_elem[0].text or None
    results['num_results_total'] =root_elem[1].text or None

    page_elem = root_elem.xpath('page')

    for page in page_elem:
        concepts = OrderedDict()
        page_num =  page[1].text or None
        results['page_num'] = page[1].text or None
        results['num_pages'] = page[2].text or None

        concept_list = page[3][0].xpath('concept')

        for concept_elem in concept_list:
            uri_concept = concept_elem[0].text
            name_concept = concept_elem[2].text
            ontology_name = concept_elem[3].text
            concepts[ uri_concept ] = [ name_concept, ontology_name ]

        results[ page_num ] = concepts

    json_results = json.dumps( results, sort_keys=False )

    return json_results


def guidedSearchS2Connector( concept_uri_list ):
    """
        guidedSearchS2Connector: Call the guidedSearchS2 API
        and extract the result from XML.

        Arguments:
            freeText (string): concept_uri list

        Returns:
            dataset (list): list of dataset grouped by concept
    """
    results = OrderedDict()

    response = requests.get( GUIDED_SEARCH_S2_API % concept_uri_list )

    doc = etree.fromstring( response.text.encode() )

    concept_list = doc

    for concept_elem in concept_list:
        dataset = OrderedDict()
        concept_uri = concept_elem.attrib['uri']

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib[ 'label' ]
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset[dataset_label] = [ num_metch, rdf_data ]

        results[concept_uri] = dataset

    json_results = json.dumps( results, sort_keys=False )

    return json_results


def guidedSearchComplexQueryConnector( concept_uri_list ):
    """
        guidedSearchComplexQueryConnector: Call the guidedSearchComplexQuery API
        and extract the result from XML.

        Arguments:
            freeText (string): concept_uri list

        Returns:
            dataset (list): list of dataset grouped by concept
    """
    results = OrderedDict()

    response = requests.get( GUIDED_SEARCH_COMPLEX_QUERY_API % concept_uri_list )

    doc = etree.fromstring( response.text.encode() )

    concept_list = doc

    for concept_elem in concept_list:
        dataset = OrderedDict()
        concept_uri = concept_elem.attrib['uri']

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib[ 'label' ]
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset[dataset_label] = [ num_metch, rdf_data ]

        results[concept_uri] = dataset

    json_results = json.dumps( results, sort_keys=False )

    return json_results
