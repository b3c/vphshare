__author__ = ""
from django.shortcuts import render_to_response
from django.template import RequestContext

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

def automaticSearchService( request ):
    """
        automaticSearch Service
    """

def guidedSearchS1Service( request ):
    """
        guidedSearch Service (Step 1)
    """

def guidedSearchS2Service( request ):
    """
        guidedSearch Service (Step 2)
    """