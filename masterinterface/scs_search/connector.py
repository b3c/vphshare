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
    dataset = []
    dict_concept = {}
    dict_dataset = {}

    response = urllib2.urlopen( AUTOMATIC_SEARCH_API % free_text )
    doc = etree.parse( response )

    concept_list = doc.findall('/concept')

    for concept_elem in concept_list:

        dict_concept['concept_uri'] = concept_elem.attrib['uri']

        dataset_list =  concept_elem.findall('dataset') or None
        if dataset_list is not None:

            for dataset_elem in dataset_list:
                dict_dataset['dataset_label'] = dataset_elem.attrib['label']
                dict_dataset['num_matches'] = dataset_elem.findtext('numMatches')
                dict_dataset['rdf_data'] = dataset_elem.findtext('rdf-data')
                dataset.append( dict_dataset )
                dict_dataset = {}

        results.append( dict_concept )
        results.append( dataset )
        dataset = []
        dict_concept = {}

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
    list_pages = []
    dict_concepts = {}

    response = urllib2.urlopen( GUIDED_SEARCH_S1_API % free_text )
    doc = etree.parse( response )

    # Adding to results max_matches and num_results_total
    root_elem = doc.find('/')
    results.append( root_elem.findtext('max_matches') or None )
    results.append( root_elem.findtext('num_results_total') or None )

    page_elem = root_elem.findall('page')
    for page in page_elem:
        # Adding to results page_num and num_pages
        list_pages.append( page.findtext('page_num') or None )
        list_pages.append( page.findtext('num_pages') or None )

        result_list_elem = page.find('content/searchResultList/')
        concept_list = result_list_elem.findall('concept')

        for concept_elem in concept_list:
            dict_concepts['uri_concept'] = concept_elem.findtext('uri_concept')
            dict_concepts['score'] = concept_elem.findtext('score')
            dict_concepts['name_concept'] = concept_elem.findtext('name_concept')
            dict_concepts['ontology_name'] = concept_elem.findtext('ontology_name')

            list_pages.append( dict_concepts )
            dict_concepts = {}

        results.append( list_pages )

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

