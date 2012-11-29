__author__ = ""

import requests
from config import *
from lxml import etree,html


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

    #response = urllib2.urlopen( AUTOMATIC_SEARCH_API % free_text )
    response = requests.get( AUTOMATIC_SEARCH_API % free_text )

    doc = etree.fromstring( response.text.encode() )

    concept_list = doc

    for concept_elem in concept_list:

        dict_concept['concept_uri'] = concept_elem.attrib['uri']

        for dataset_elem in concept_elem:
            dict_dataset['dataset_label'] = dataset_elem.attrib['label']
            dict_dataset['num_matches'] = dataset_elem[0].text
            dict_dataset['rdf_data'] = dataset_elem[1].text
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

    response = requests.get( GUIDED_SEARCH_S1_API % free_text )
    doc = etree.fromstring( response.text.encode() )

    # Adding max_matches and num_results_total to results
    root_elem = doc

    results.append( root_elem[0].text or None )
    results.append( root_elem[0].text or None )

    page_elem = root_elem.xpath('page')

    for page in page_elem:
        # Adding page_num and num_pages to list_pages
        list_pages.append( page[0].text or None )
        list_pages.append( page[1].text or None )

        concept_list = page[2][0].xpath('concept')

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

