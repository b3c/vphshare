from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from permissions.models import PrincipalRoleRelation

from piston.handler import BaseHandler
from piston.utils import rc

from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs_resources.models import Resource

import base64
import json
import requests
from urlparse import urlparse
import itertools

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class EJobException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        # if I need custom params then after this

class EJob(models.Model):
    """Job model for external job queue
    """
    ST_SUBMITED = 0
    ST_STARTED = 1
    ST_CANCELLED = 2
    ST_COMPLETED = 3
    ST_FAILED = 4
    FSM_STATES = (
        (ST_SUBMITED,"Submited"),
        (ST_STARTED,"Started"),
        (ST_CANCELLED,"Cancelled"),
        (ST_COMPLETED,"Completed"),
        (ST_FAILED,"Failed"),
    )

    # given by default using djando.models
    # id = models.AutoField(primary_key=True)

    # it's not going to be necesary
    # task_id = models.CharField(unique=True, null=True, max_length=39)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    modification_timestamp = models.DateTimeField(auto_now=True)
    state = models.PositiveIntegerField(choices=FSM_STATES,default=ST_SUBMITED)
    message = models.CharField(max_length=1024,default="")
    input_data = models.TextField(max_length=4096,default="")
    output_data = models.TextField(max_length=4096,default="")
    owner_id = models.BigIntegerField()
    worker_id = models.BigIntegerField()

def ejob_submit(owner_id, worker_id, payload={}):
    # create object
    # return True if success else EJobException is raised
    # raise EJobException("error message")
    if worker_id == -1:
        raise EJobException("failed to create ejob with worker_id -1")
    ej = EJob(message=payload.get("message",""),input_data=json.dumps(payload.get("data",{})),
            owner_id=owner_id,worker_id=worker_id)
    ej.save()
    return ej

def ejob_transit(job_id, worker_id, next_state):
    # get job and check if same worker
    # ckeck next state exists and transit
    # return True if success else EJobException is raised
    # raise EJobException("error message")
    pass

def ejob_cancel(job_id, owner_id):
    # get job and check if same owner
    # transit to cancel state
    # return True if success else EJobException is raised
    # raise EJobException("error message")
    ej = EJob.objects.get(Q(id__exact=job_id),Q(owner_id__exact=owner_id))
    if ej.state() <= EJob.ST_STARTED:
        ej.state(EJob.ST_CANCELLED)
        ej.save()

    return ej

