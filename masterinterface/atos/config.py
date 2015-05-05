"""
    scs_search: config.py Module
"""
__author__ = 'a.saglimbeni@scsitaly.com'
from django.conf import settings
# Semantica api urls and configurations

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

DATASET_SCHEMA = 'http://vphshare.atosresearch.eu/crawling/rest/schema'

CLASSES_TABLES = 'http://vphshare.atosresearch.eu/crawling/rest/schema/classesTables?datasetName=%s'

PROPERTIES_RANGES = 'http://vphshare.atosresearch.eu/crawling/rest/schema/propertiesRanges?datasetName=%s' \
                    '&conceptURI=%s'

OBJECT_PROPERTIES_RANGES = 'http://vphshare.atosresearch.eu/crawling/rest/schema/objectPropertiesRanges?datasetName=%s&' \
                           'conceptURI=%s'

INDIVIDUALS = 'http://vphshare.atosresearch.eu/crawling/rest/schema/individuals?datasetName=%s&conceptURI=%s'

DATA_PROPERTIES_RANGES = 'http://vphshare.atosresearch.eu/crawling/rest/schema/dataPropertiesRanges?datasetName=%s&' \
                         'conceptURI=%s'

# Metadata api urls

GLOBAL_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata'

RESOURCE_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/%s'

FACETS_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/facets/%s/%s?value=%s&numResults=%s&page=%s&orderBy=%s&orderType=%s'

TYPE_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/facets/%s?numResults=%s&page=%s&orderBy=%s&orderType=%s'

FILTER_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/filter?logicalExpression=%s&numResults=%s&page=%s&orderBy=%s&orderType=%s'

FILTER_METADATA_BY_GLOBALID = settings.ATOS_METADATA_URL + '/rest/metadata/filter?params=name,description,tags&text=%s&logicalExpression=%s&numResults=%s&page=%s&orderBy=%s&orderType=%s'

SEARCH_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/multifield?params=name,description,tags&text=%s&numResults=%s&page=%s&orderBy=%s&orderType=%s'
#SEARCH_METADATA_API = settings.ATOS_METADATA_URL + '/rest/metadata/multifield?params=name,description,tags&text=%s'

FACETS_LIST = [u'type', u'name', u'description', u'author', u'category', u'tags', u'semantic_annotations', u'licence', u'rating', u'views', u'local_id']

EMPTY_LIST = {"page": 0,
                "pages": 0,
                "fileCount": 0,
                "atsCount": 0,
                "swsCount": 0,
                "wfCount": 0,
                "wsCount": 0,
                "datasetCount": 0,
                "resource_metadata": [],
                "numCurrentPageMetadata": 0,
                "numTotalMetadata": 0}