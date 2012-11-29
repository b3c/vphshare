__author__ = ""
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from piston.handler import BaseHandler
from connector import automaticSearchConnector
from connector import guidedSearchS1Connector

def automaticSearchView( request ):
    """
        automaticSearch view
    """

    return render_to_response("scs_search/scs_search.html",
        None,
        RequestContext(request))


def guidedSearchView( request ):
    """
        guidedSearch view
    """

    return render_to_response("scs_search/scs_search.html",
        None,
        RequestContext(request))


class AutomaticSearchService( BaseHandler ):
    """
    """

    allowed_methods = ('POST', 'GET')

    def create(self, request):
        """
            call on POST
        """
        if request.method == "POST":

            free_text = request.POST['input']
            connector = automaticSearchConnector( free_text )

            return connector

        response = HttpResponse(status=403)
        response._is_string = True

        return response


    def read( self, request ):
        """
            call on GET
        """
        pass



class GuidedSearchS1Service( BaseHandler ):
    """
    """

    allowed_methods = ('POST', 'GET')

    def create(self, request):
        """
            call on POST
        """
        if request.method == "POST":

            free_text = request.POST['input']
            connector = guidedSearchS1Connector( free_text )

            return connector

        response = HttpResponse(status=403)
        response._is_string = True

        return response



class GuidedSearchS2Service( BaseHandler ):
    """
    """

    allowed_methods = ('POST', 'GET')

    def create(self, request):
        """
            call on POST
        """
        if request.method == "POST":

            concept_uri_list = request.POST['concept_uri_list']
            connector = guidedSearchS1Connector( concept_uri_list )

            return connector

        response = HttpResponse(status=403)
        response._is_string = True

        return response