from django.db import models
from django.core.cache import cache as cc
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.conf import settings

from masterinterface.scs_resources.models import Resource

import json
import requests
import StringIO
import csv
import hashlib as hl
from lxml import etree, objectify
import xml.dom.minidom as dom
import collections as colls
import logging

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("{0}/{1}.log".format("/tmp", __name__))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

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
        """call send_data_insersect_summary and get metadata foreach guid
            returns a tuple with ([guids],[datasets objs])
        """
        rel_guids = self.send_data_intersect_summary(ticket)
        rel_dss = []
        for guid in rel_guids:
            ds = Resource.objects.get(global_id=guid)
            ds.load_additional_metadata(ticket)
            # TODO XXX
            # ds["publishaddress"] = 
            # ds["dbname"] = 
            rel_dss.append(ds)

        return (rel_guids,rel_dss)


    def send_data_intersect_summary(self, ticket):
        """get related dbs using global_id.
            returns: [] if not related datasets else a [] with their global_id
        """
        dataset_id = self.global_id
        dss = [dataset_id,]

        if settings.FEDERATE_QUERY_URL:
            try:
                logger.debug("send_data_intersect_summary dataset gid: ", dataset_id)
                results = requests.post("%s/DataIntersectSummary" % 
                            (settings.FEDERATE_QUERY_URL,) ,
                              data="datasetGUID=%s" % (dataset_id,),
                              auth=("admin", ticket),
                              headers = {'content-type': 'application/x-www-form-urlencoded'},
                              verify=False
                              ).content

                # xml parsing
                xml_tree = objectify.fromstring(results)
                dss = list(set(dss).union([ el.text.split("|")[0] for el in xml_tree.string if xml_tree.countchildren() > 0 ]))
            except Exception, e:
                logger.exception(e)
            finally:
                return dss

            logger.debug("send_data_intersect_summary: ",str(dss))

        else:
            logger.error("FEDERATE_QUERY_URL var in settings.py doesn't exist")
            return dss


    def send_query(self, ticket):
        """
        """
        json_query = json.loads(self.query)
        dataset = Resource.objects.get(global_id=self.global_id)
        (_, rel_datasets) = self.send_data_intersect_summary_with_metadata(ticket)
        data = {
            "dataset": dataset,
            "rel_datasets": rel_datasets,
            "select": json_query["select"],
            "where": json_query["where"]
        }

        # getting hex sha1 id
        sha1_input = self.global_id + ":" + str( ticket ) + ":" + str( json_query )
        sha1_id = hl.sha1(sha1_input.encode()).hexdigest()

        # check from cache
        cached_query = cc.get(sha1_id)
        if cached_query is None:
            if settings.FEDERATE_QUERY_SOAP_URL:
                xml_query = render_to_response("datasets/query_template.xml", data)
                logger.debug( str(xml_query) )

                results = requests.post(
                            "%s/xmlquery/DatasetSOAPQuery.asmx" % (settings.FEDERATE_QUERY_SOAP_URL,),
                              data=xml_query.content,
                              auth=("admin", ticket),
                              headers = {'content-type': 'text/xml', 
                                        'SOAPAction': 'http://vph-share.eu/dms/FederatedQuery'},
                              verify=False
                ).content
                
                root = dom.parseString(results)
                cached_results = root.getElementsByTagName("FederatedQueryResult")[0].\
                        childNodes[0].\
                        data.\
                        strip()

                if len(cached_results.split(" ")) > 1:
                    cc.set(sha1_id, cached_results, 60)
                    return cached_results
                else:
                    return ""

            else:
                logger.error("FEDERATE_QUERY_SOAP_URL var in settings.py doesn't exist")
                return ""


        else:
            return cached_query

    def get_header(self, ticket):
        csv_results = self.send_query(ticket)
        return csv.reader(StringIO.StringIO(csv_results)).next()

    def get_results(self, ticket):
        csv_results = csv.reader(StringIO.StringIO(self.send_query(ticket)))
        #ignore the first header row
        csv_results.next()
        return [ row for row in csv_results ]

    def get_results_number(self, ticket):
        """
        """
        csv_results = self.send_query(ticket)
        return len(StringIO.StringIO(csv_results).readlines())





