__author__ = 'Ernesto Coto'
from piston.handler import BaseHandler, AnonymousBaseHandler
from wfmng_api.models import WfMngApiModel
from masterinterface.scs_auth.auth import authenticate 
from piston.utils import rc
from wfmng import *
import requests
import json
import base64
import random

# SAMPLE POST
# curl -X POST -H "MI-TICKET:dWlkPWVjb3RvO3ZhbGlkdW50aWw9MTM5NDUwMzQwNztjaXA9MC4wLjAuMDt0b2tlbnM9YWRtaW4sdGVzdCxEZXZlbG9wZXIsdnBoLGRldmVsb3BlcixWUEg7dWRhdGE9ZWNvdG8sRXJuZXN0byBDb3RvLGUuY290b0BzaGVmZmllbGQuYWMudWssLFVOSVRFRCBLSU5HRE9NLFMxNEVUO3NpZz1NQzBDRkd1TWE5cHVMeU1aRW91STlmRXArdjFuNFM4akFoVUF3NjdCM3lLUExIa2djKzRlYWlXYVJzMWNlUkE9" "http://127.0.0.1:8000/wfmng/submit/" -F "global_id=b32e64f7-5897-4c9e-b8d5-cc7365edece2"

# SAMPLE GET
# curl -X GET -H "MI-TICKET:dWlkPWVjb3RvO3ZhbGlkdW50aWw9MTM5NDIyNjM3MTtjaXA9MC4wLjAuMDt0b2tlbnM9YWRtaW4sdGVzdCxEZXZlbG9wZXIsdnBoLGRldmVsb3BlcixWUEg7dWRhdGE9ZWNvdG8sRXJuZXN0byBDb3RvLGUuY290b0BzaGVmZmllbGQuYWMudWssLFVOSVRFRCBLSU5HRE9NLFMxNEVUO3NpZz1NQ3dDRkFqc3MydTUwUDZualUrK0FoYWxRMEtYZzlqakFoUVNTRkdiUmVXeEw3V0RyMEd3eVJ4ZUJpU0NPQT09" "http://127.0.0.1:8000/wfmng/aa878a13-7b2a-4e34-8e8c-8102d439427a?instance_id=1814"

# SAMPLE DELETE
# curl -X DELETE -H "MI-TICKET:dWlkPWVjb3RvO3ZhbGlkdW50aWw9MTM5NDIyNjM3MTtjaXA9MC4wLjAuMDt0b2tlbnM9YWRtaW4sdGVzdCxEZXZlbG9wZXIsdnBoLGRldmVsb3BlcixWUEg7dWRhdGE9ZWNvdG8sRXJuZXN0byBDb3RvLGUuY290b0BzaGVmZmllbGQuYWMudWssLFVOSVRFRCBLSU5HRE9NLFMxNEVUO3NpZz1NQ3dDRkFqc3MydTUwUDZualUrK0FoYWxRMEtYZzlqakFoUVNTRkdiUmVXeEw3V0RyMEd3eVJ4ZUJpU0NPQT09" "http://127.0.0.1:8000/wfmng/aa878a13-7b2a-4e34-8e8c-8102d439427a?instance_id=1814&ts_id=1334"

class WfMngApiHandler(BaseHandler):
    """
    REST service based on Django-Piston Library
    """
    model = WfMngApiModel

    def create(self, request, *args, **kwargs):
        """
        Submits the workflow with the `global_id` specified in the request, and starts its execution.
        
        Parameters:
         - `request`: request
         - `args`: args
         - `kwargs`: kwargs
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    pass #return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if request.method == 'POST':
                if request.POST.get('global_id', None)==None:
                    return rc.BAD_REQUEST
                #print request.POST['global_id']
                global_id = request.POST['global_id']
                #if global_id:
                #    dbWorkflow = Workflow.objects.get(global_id=global_id)
                #else:
                #    return rc.BAD_REQUEST
                #if dbWorkflow.owner != user:
                #    response = HttpResponse(status=403)
                #    response._is_string = True
                #    return response   
                wf_definition = ""
                input_definition = ""
                try:
                    headers = {'MI-TICKET': ticket}
                    con = requests.get(
                        "http://devel.vph-share.eu/api/workflows/%s/" % (global_id),
                        headers=headers,
                        verify = False
                    )
                    
                    if con.status_code in [200, 201, 204]:
                        json = con.json()
                        input_definition = base64.b64decode(json['input_definition'])
                        wf_definition = base64.b64decode(json['t2flow']) 

                except Exception as e:
                    print e
                    pass
                if wf_definition!= "" and input_definition!= "":
                    #print "Execute workflow " + global_id
                    eid = random.randint(90000, 100000)
                    wfRunSuccess = execute_workflow(ticket, eid, "Execution Test %s" % str(eid), "223", wf_definition, input_definition)
                    if wfRunSuccess=='True':
                        return eid
                return rc.INTERNAL_ERROR
        except Exception, e:
            #print e
            return rc.INTERNAL_ERROR


    def read(self,  request, wfrun_id=None):
        """
        Get the information about the workflow run specified in the request.
        
        Parameters:
         - `request`: request
         - `wfrun_id`: workflow run id
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    pass #return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if wfrun_id:
                return getWorkflowInformation(wfrun_id, ticket)
            return rc.BAD_REQUEST
        except Exception, e:
            print e
            return rc.INTERNAL_ERROR


    def delete(self, request, wfrun_id=None):
        """
        Deletes the workflow run specified in the request
        
        Parameters:
         - `request`: request
         - `wfrun_id`: workflow run id
        """
        try:
            client_address = request.META['REMOTE_ADDR']
            ticket = request.META.get('HTTP_MI_TICKET', '')
            if ticket:
                try:
                    user, tkt64 = authenticate(ticket=ticket, cip=client_address)
                except Exception, e:
                    pass #return rc.FORBIDDEN
            else:
                return rc.FORBIDDEN
            if wfrun_id:
                return stopWorkflow(wfrun_id, ticket)
            return rc.BAD_REQUEST
        except Exception, e:
            print e
            return rc.INTERNAL_ERROR
