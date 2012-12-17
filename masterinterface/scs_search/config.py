"""
    scs_search: config.py Module
"""
__author__ = ''

AUTOMATIC_SEARCH_API = \
    'http://vphshare.atosresearch.eu/semantic-retrieval/rest/data/' \
    'full-search/triples?keywords=%s'

GUIDED_SEARCH_S1_API = \
    'http://vphshare.atosresearch.eu/semantic-retrieval/rest/data/' \
    'guided-search/terms?keywords=%s&nummaxhits=%s&pagesize=%s&pagenum=%s'

GUIDED_SEARCH_S2_API = \
    'http://vphshare.atosresearch.eu/semantic-retrieval/rest/data/' \
    'guided-search/triples?terms=%s'

GUIDED_SEARCH_COMPLEX_QUERY_API = \
    'http://vphshare.atosresearch.eu/semantic-retrieval/rest/data/' \
    'guided-search/complex_triples?terms=%s'

PAGE_SIZE = 20
