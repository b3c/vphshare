from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.cache import cache

from masterinterface.scs_resources.models import Resource

import json
import requests
import StringIO
import csv
import hashlib as hl
from lxml import etree, objectify
import xml.dom.minidom as dom
from urlparse import urlparse
import itertools
import logging

logger = logging.getLogger()

fake_csv = """"date_of_birth","waist","smoker","FixedIM","gender","MovedIM","First_Name","weight","Last_Name","country","address","PatientID","autoid"
NULL,38.65964957,2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0320.dcm",2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0408.dcm","Dalton",51.98509226,"Coleman","Virgin Islands, British","Ap #700-2897 Dolor, Road","jRRhMftJ2qtV2Uco9C/E9/nUhqA=",1
NULL,33.79895416,2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0325.dcm",2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0423.dcm","Boris",57.52852986,"Joyce","Samoa","Ap #692-9994 Cubilia Av.","8uk6ZFL/xGQ1BxrCezVgxwuuqLE=",2
NULL,32.1578081,4,"C:\Users\smwood\Work\Y3Review\dicom\IM_0377.dcm",1,"C:\Users\smwood\Work\Y3Review\dicom\IM_0431.dcm","Freya",52.23334131,"Hebert","Slovenia","112-5252 Ante. Street","nIPF979pRagHMUGMnjSi1aKNMeA=",3
NULL,34.5336565,1,"C:\Users\smwood\Work\Y3Review\dicom\IM_0383.dcm",1,"C:\Users\smwood\Work\Y3Review\dicom\IM_0433.dcm","Hop",50.53191368,"Singleton","Benin","Ap #541-9922 Phasellus St.","KUyWW/F60KyyDX20reEZtPHZTlM=",4
NULL,36.0445105,2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0389.dcm",2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0436.dcm","Malcolm",45.21699134,"Becker","Guinea-Bissau","P.O. Box 168, 5437 Euismod St.","MGpFSDGTzCrCb3Xp3wA0c2fwWD0=",5
NULL,39.05727324,4,"C:\Users\smwood\Work\Y3Review\dicom\IM_0390.dcm",2,"C:\Users\smwood\Work\Y3Review\dicom\IM_0439.dcm","Quynn",50.99911053,"Boyle","Turkmenistan","989-6482 Viverra. Road","o5sBdZVEPoLAwXjoXCFqGZqBkA0=",6
NULL,39.14665053,4,"C:\Users\smwood\Work\Y3Review\dicom\IM_0397.dcm",1,"C:\Users\smwood\Work\Y3Review\dicom\IM_0442.dcm","Hilel",42.97475325,"Blackwell","Jordan","379-2236 A, St.","/PLXF2HHJwLFjX3PkstH0lYOUV8=",7
NULL,35.25776665,1,"C:\Users\smwood\Work\Y3Review\dicom\IM_0400.dcm",1,"C:\Users\smwood\Work\Y3Review\dicom\IM_08012.dcm","Micah",45.5508206,"Mejia","Taiwan","1987 Dictum Rd.","/1Cadddh53zzn1k8PAjYjIdtuvw=",8
NULL,35.40281641,3,"C:\Users\smwood\Work\Y3Review\dicom\IM_0407.dcm",1,"C:\Users\smwood\Work\Y3Review\dicom\IM_08014.dcm","Desiree",60.84924424,"Casey","United Kingdom (Great Britain)","Ap #658-4631 Primis Avenue","l3bVOw3HHgkNmqbXKP0a/Azbo9U=",9"""

class DatasetQuery(models.Model):
    """
    """

    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, default="")
    user = models.ManyToManyField(User)
    query = models.TextField()
    global_id = models.CharField(null=True, max_length=39)


    def __unicode__(self):
        return self.name

    def send_data_intersect_summary_with_metadata(self, ticket):
        """call send_data_insersect_summary and get metadata foreach (guid,subjectnumber)
            returns a tuple with ([guids],[datasets objs])
        """
        rel_guids = self.send_data_intersect_summary(ticket)
        rel_dss = []
        for guid in rel_guids:
            ds = Resource.objects.get(global_id=guid[0])
            ds.load_additional_metadata(ticket)
            if ds.metadata is not None:
                (paddress, dbname) = _url_parse(ds.metadata["localID"])
                ds.metadata["publishaddress"] = paddress
                ds.metadata["dbname"] = dbname
                ds.metadata["sharedsubjects"] = guid[1]
                rel_dss.append(ds)

        return (rel_guids,rel_dss)


    def send_data_intersect_summary(self, ticket):
        """get related dbs using global_id.
            returns: [] if not related datasets else a [] with their global_id
        """
        dataset_id = self.global_id
        dss = [ ( dataset_id,0 ) ]
        dss_tmp = []

        if settings.FEDERATE_QUERY_URL:

            # getting from cache
            key = _get_hash_key("fq:", str(self.global_id), str(ticket))
            from_cache = cache.get(key)

            if from_cache is None:
                try:
                    results = requests.post("%s/DataIntersectSummary" %
                                (settings.FEDERATE_QUERY_URL,) ,
                                  data="datasetGUID=%s" % (dataset_id,),
                                  auth=("admin", ticket),
                                  headers = {'content-type': 'application/x-www-form-urlencoded'},
                                  verify=False
                                  ).content

                    # xml parsing
                    xml_tree = objectify.fromstring(results)
                    dss_tmp = list(set(dss_tmp).union( [ ( el.text.split("|")[0],el.text.split("|")[1] ) \
                                                        for el in xml_tree.string \
                                                            if xml_tree.countchildren() > 0 ]))

                    if len(dss_tmp) > 0:
                        dss = dss_tmp
                        cache.set(key,dss,300)

                except Exception, e:
                    logger.exception(e)

                finally:
                    return dss

            else:
                dss = from_cache
                return dss

        else:
            logger.error("FEDERATE_QUERY_URL var in settings.py doesn't exist")
            return dss


    def send_query(self, ticket):
        """
        """
        json_query = json.loads(self.query)

        (_test, rel_datasets) = \
            self.send_data_intersect_summary_with_metadata(ticket)

        dataset = [ el for el in rel_datasets if el.global_id == self.global_id ]
        data = {
            "dataset": dataset[0],
            "rel_datasets": rel_datasets,
            "select": json_query["select"],
            "where": json_query["where"]
        }

        if settings.FEDERATE_QUERY_SOAP_URL:
            try:
                key = _get_hash_key(str(self.global_id),
                        str(sorted(_test)),
                        str(sorted(json_query.items())) )

                from_cache = cache.get(key)

                if from_cache is None:
                    cached_results = self._query_request(ticket, json_query, data)
                    cache.set(key,cached_results,300)

                    return cached_results

                else:
                    return from_cache

            except Exception, e:
                logger.exception(e)
                return ""

        else:
            logger.error("FEDERATE_QUERY_SOAP_URL var in settings.py doesn't exist")
            return ""


    def get_header(self, ticket):
        csv_results = self.send_query(ticket)

        if csv_results:
            reader = csv.reader(StringIO.StringIO(csv_results))
            header = [el for el in reader]
            return header[0]

        else:
            return []

    def get_results(self, ticket):
        data = self.send_query(ticket)

        if data:
            csv_results = csv.reader(StringIO.StringIO(data))
            csv_results.next()
            data = [ row for row in csv_results ]
            return data
        else:
            return []

    def get_results_number(self, ticket):
        """
        """
        csv_results = self.send_query(ticket)

        if csv_results:
            return len(StringIO.StringIO(csv_results).readlines())
        else:
            return 0


    def get_query_data(self, ticket):
        data = self.send_query(ticket)

        if data:
            csv_results = csv.reader(StringIO.StringIO(data))
            data = [ row for row in csv_results ]
            return data
        else:
            return []

    def _query_request(self, ticket, query_dict, data):
        """request single query or fed query
            returns request .content response
        """
        results = ""
        if _check_if_simple_query(query_dict):
            xml_query = render_to_response("datasets/query_single_template.xml", data)

            single_dataset = data["dataset"]
            if single_dataset.metadata["localID"][-1] != "/":
                single_dataset.metadata["localID"] = single_dataset.metadata["localID"] + "/"

            results = requests.post(
                    "%sxmlquery/DatasetSOAPQuery.asmx" % (single_dataset.metadata["localID"],),
                    data=xml_query.content,
                    auth=("admin", ticket),
                    headers = {'content-type': 'text/xml',
                        'SOAPAction': 'http://vph-share.eu/dms/Query'},
                    verify=False
                    ).content

            # parsing xml like dom to get result
            root = dom.parseString(results)
            results = root.getElementsByTagName("QueryResult")[0].\
                    childNodes[0].\
                    data.\
                    strip().rstrip('\r\n')

        else:
            xml_query = render_to_response("datasets/query_template.xml", data)

            results = requests.post(
                    "%s/xmlquery/DatasetSOAPQuery.asmx" % (settings.FEDERATE_QUERY_SOAP_URL,),
                    data=xml_query.content,
                    auth=("admin", ticket),
                    headers = {'content-type': 'text/xml',
                        'SOAPAction': 'http://vph-share.eu/dms/FederatedQuery'},
                    verify=False
                    ).content

            root = dom.parseString(results)
            results = root.getElementsByTagName("FederatedQueryResult")[0].\
                    childNodes[0].\
                    data.\
                    strip().rstrip('\r\n')

        # happy return
        return results


def _check_if_simple_query(query):
    """if query contains only 1 dataset then function return True
    otherwise return False
    """
    flatted = list(itertools.chain.from_iterable(
        [ el["group"] for el in query["where"] if "where" in query ] ) )

    return len(set( [ el["datasetname"] for el in query["select"] if "select" in query ] +
        [ el["datasetname"] for el["group"] in flatted ] ) ) == 1

def _url_parse(uri):
    """ return tuple (host, 1st path without slash )"""
    host = ""
    path = ""

    p_uri = urlparse(uri)
    host = p_uri.netloc
    path = p_uri.path.rstrip('/').strip('/')

    return (host,path)

def _get_hash_key(data, *args):
    """get sha1 sum hexdigest for a string"""
    return hl.sha1( ":".join([data] + [el for el in args]) ).hexdigest()
