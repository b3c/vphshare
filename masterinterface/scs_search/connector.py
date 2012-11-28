__author__ = ""

import urllib2
from config import *
from lxml import etree


def automaticSearchConnector( free_text ):
    """
        automaticSearchConnector: Call the automaticSearch API
        and extract the result from XML.

        Arguments:
            freeText (string): input text

        Returns:
            dataset (list): list of dataset grouped by concept_uri

    """
    results = []
    dict = {}

    response = urllib2.urlopen( AUTOMATIC_SEARCH_API % free_text )
    doc = etree.parse(response)

    concept_list = doc.findall('/concept')

    for concept_elem in concept_list:

        dict['concept_uri'] = concept_elem.attrib['uri']

        dataset_list =  concept_elem.findall('dataset') or None
        if dataset_list is not None:

            for dataset_elem in dataset_list:
                dict['dataset_label'] = dataset_elem.attrib['label']
                dict['num_matches'] = dataset_elem.findtext('numMatches')
                dict['rdf_data'] = dataset_elem.findtext('rdf-data')

        results.append( dict )
        dict = {}

    return results


def guidedSearchS1Connector( free_text ):
    """
        guidedSearchS1Connector: Call the guidedSearchS1 API
        and extract the result from XML.

        Arguments:
            freeText (string): input text

        Returns:
            dataset (list): list of concept/terms
    """
    results = []
    dict = {}

    response = urllib2.urlopen( GUIDED_SEARCH_S1_API % free_text )
    doc = etree.parse(response)

    # Adding to results max_matches and num_results_total
    root_elem = doc.find('/')
    results.append( root_elem.findtext('max_matches') or None )
    results.append( root_elem.findtext('num_results_total') or None )

    # Adding to results page_num and num_pages
    page_elem = root_elem.find('page')
    results.append( page_elem.findtext('page_num') or None )
    results.append( page_elem.findtext('num_pages') or None )

    result_list_elem = page_elem.find('content/searchResultList/')
    concept_list = result_list_elem.findall('concept')

    for concept_elem in concept_list:
        dict['uri_concept'] = concept_elem.findtext('uri_concept')
        dict['score'] = concept_elem.findtext('score')
        dict['name_concept'] = concept_elem.findtext('name_concept')
        dict['ontology_name'] = concept_elem.findtext('ontology_name')

        results.append( dict )
        dict = {}

    return results



def guidedSearchS2Connector( concept_uri_list ):
    """
        guidedSearchS2Connector: Call the guidedSearchS1 API
        and extract the result from XML.

        Arguments:
            freeText (string): concept_uri list

        Returns:
            dataset (list): list of dataset grouped by concept
    """

