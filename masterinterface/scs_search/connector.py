"""
    scs_search: connector.py Module
"""
__author__ = ''

import requests
import json
from config import *
from lxml import etree
from ordereddict import OrderedDict
from urllib import quote


def automatic_search_connector( free_text ):
    """
        automatic_search_connector: Call the automatic search API
        and extract the result from XML.

        Arguments:
            free-text (string): input text

        Returns:
            json_results (obj): object JSON format

    """

    results = OrderedDict()

    response = requests.get( AUTOMATIC_SEARCH_API % free_text )

    concept_list = etree.fromstring( response.text.encode() )

    for concept_elem in concept_list:
        dataset_dict = OrderedDict()
        concept_uri = concept_elem.attrib[ 'uri' ]

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib[ 'label' ]
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset_dict[ dataset_label ] = [ num_metch, rdf_data ]

        results[ concept_uri ] = dataset_dict

    return results


def guided_search_s1_connector( free_text, num_max_hits, page_num ):
    """
        guided_search_S1_Connector: Call the guided Search step1 API
        and extract the result from XML.

        Arguments:
            freeText (string): input text
            num_max_hits (integer): number oh results
            page_num (integer): page number

        Returns:
            json_results (obj): object JSON format
    """

    results = OrderedDict()

    response = requests.get( GUIDED_SEARCH_S1_API % ( free_text,
                            num_max_hits, PAGE_SIZE, page_num ) )
    root_elem = etree.fromstring( response.text.encode() )

    results[ 'max_matches' ] = root_elem[0].text or None
    results[ 'num_results_total' ] = root_elem[1].text or None

    page_elem = root_elem.xpath( 'page' )

    for page in page_elem:
        concepts = OrderedDict()
        page_num = page[1].text or None
        results[ 'page_num' ] = page[1].text or None
        results[ 'num_pages' ] = page[2].text or None

        concept_list = page[3][0].xpath( 'concept' )

        for concept_elem in concept_list:
            uri_concept = concept_elem[0].text
            name_concept = concept_elem[2].text
            ontology_name = concept_elem[3].text
            concepts[ uri_concept ] = [ name_concept, ontology_name ]

        results[ page_num ] = concepts

    json_results = json.dumps( results, sort_keys = False )

    return json_results


def guided_search_s2_connector( concept_uri_list ):
    """
        guided_search_S2_connector: Call the guided search step2 API
        and extract the result from XML.

        Arguments:
            concept_uri_list (string): concept_uri list

        Returns:
            json_results (obj): object JSON format
    """

    results = OrderedDict()

    response = requests.get( GUIDED_SEARCH_S2_API % concept_uri_list )

    concept_list = etree.fromstring( response.text.encode() )

    for concept_elem in concept_list:
        dataset = OrderedDict()
        concept_uri = concept_elem.attrib[ 'uri' ]

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib[ 'label' ]
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset[ dataset_label ] = [ num_metch, rdf_data ]

        results[ concept_uri ] = dataset

    json_results = json.dumps( results, sort_keys = False )

    return json_results


def complex_query_connector( load_groups ):
    """
        guided_search_complex_query_connector: Call the guided search ComplexQuery API
        and extract the result from XML.

        Arguments:
            concept_uri_list (string): concept_uri list

        Returns:
            json_results (obj): object JSON format
    """

    results = OrderedDict()
    terms = ""

    for ( j, group ) in enumerate( load_groups ):

        if j == 0:
            if group[0] == "NOT":
                if ( len( group ) - 1 )  > 1:
                    for ( i, concept ) in enumerate( group ):
                        if concept != "NOT":
                            if i < ( len( group ) - 1 ) and i == 1:
                                terms = terms + ' ( NOT ' + concept[0] + ' ) AND '
                            elif i < ( len( group ) - 1 ):
                                terms = terms + '( NOT ' + concept[0] + ' ) AND '
                            else:
                                terms = terms + '( NOT ' + concept[0] + ' ) '
            else:
                if ( len( group ) - 1 )  > 1:
                    for ( i, concept ) in enumerate( group ):
                        if concept != "":
                            if i < ( len( group ) - 1 ) and i == 1:
                                terms = terms + ' ( ' + concept[0] + ' OR '
                            elif i < ( len( group ) - 1 ):
                                terms = terms + concept[0] + ' OR '
                            else:
                                terms = terms + concept[0] + ' ) '
                else:
                    terms = terms + ' ( ' + group[0] + ' ) '

        else:
            if group[0] == "NOT":
                if ( len( group ) - 1 )  > 1:
                    for ( i, concept ) in enumerate( group ):
                        if concept != "NOT":
                            if i < ( len( group ) - 1 ) and i == 1:
                                terms = terms + 'AND ( NOT ' + concept[0] + ' ) AND '
                            elif i < ( len( group ) - 1 ):
                                terms = terms + '( NOT ' + concept[0] + ' ) AND '
                            else:
                                terms = terms + '( NOT ' + concept[0] + ' ) '
            else:
                if ( len( group ) - 1 )  > 1:
                    for ( i, concept ) in enumerate( group ):
                        if concept != "":
                            if i < ( len( group ) - 1 ) and i == 1:
                                terms = terms + 'AND ( ' + concept[0] + ' OR '
                            elif i < ( len( group ) - 1 ):
                                terms = terms + concept[0] + ' OR '
                            else:
                                terms = terms + concept[0] + ' ) '
                else:
                    terms = terms + ' ( ' + group[0] + ' ) '


    response = requests.get( GUIDED_SEARCH_COMPLEX_QUERY_API
                            % quote(terms) )

    concept_list = etree.fromstring( response.text.encode() )

    for concept_elem in concept_list:
        dataset = OrderedDict()
        concept_uri = concept_elem.attrib[ 'logicalExpression' ]

        for dataset_elem in concept_elem:
            dataset_label = dataset_elem.attrib['label']
            num_metch = dataset_elem[0].text
            rdf_data = dataset_elem[1].text
            dataset[ dataset_label ] = [ num_metch, rdf_data ]

        results[ concept_uri ] = dataset

    return results


