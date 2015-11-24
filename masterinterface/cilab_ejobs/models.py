__author__ = 'Miguel C.'
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from masterinterface.scs_auth import models as scs_models
import copy

import json
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
    ST_CURATED = 5
    FSM_STATES = (
        (ST_SUBMITED,"Submited"),
        (ST_STARTED,"Started"),
        (ST_CANCELLED,"Cancelled"),
        (ST_COMPLETED,"Completed"),
        (ST_FAILED,"Failed"),
        (ST_CURATED,"Curated"),
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
    owner_name = models.CharField(max_length=128,default=False)
    worker_name = models.CharField(max_length=128,default=False)
    auto_run = models.BooleanField(default=False)

def ejob_submit(owner_id, worker_id, payload={}):
    """"create object

    return True if success else EJobException is raised
    raise EJobException("error message")
    """
    if worker_id == -1:
        raise EJobException("failed to create ejob with worker_id -1")

    oname = scs_models.User.objects.get(id=owner_id).username
    wname = scs_models.User.objects.get(id=worker_id).username

    ej = EJob(message=payload.get("message",""),
            input_data=json.dumps(payload.get("data",{})),
            auto_run=payload.get("auto_run",False),
              owner_id=owner_id,worker_id=worker_id,
              owner_name=oname,worker_name=wname)
    ej.save()
    return ej

def ejob_transit(job_id, worker_id, data):
    """get job and check if same worker

    ckeck next state exists and transit
    return transited ejob if success else EJobException is raised
    raise EJobException("error message")
    """
    submited_nstates = set([EJob.ST_STARTED])
    started_nstates = set([EJob.ST_STARTED, EJob.ST_COMPLETED, EJob.ST_FAILED])
    completed_nstates = set([EJob.ST_FAILED, EJob.ST_CURATED])

    ej = EJob.objects.get(Q(id__exact=job_id),Q(worker_id__exact=worker_id))

    tmp_dict = json.loads( '{}' if not ej.output_data else ej.output_data )
    data_dict = tmp_dict.copy()
    next_state = data["state"]
    data_dict.update(data.get("data",{}))
    output_data = json.dumps(data_dict)

    st = ej.state
    # start or cancel
    if st == EJob.ST_SUBMITED and next_state in submited_nstates:
        ej.state = next_state
        ej.output_data = output_data
        ej.save()

    # finish or cancel
    elif st == EJob.ST_STARTED and next_state in started_nstates:
        ej.state = next_state
        ej.output_data = output_data
        ej.save()

    elif st == EJob.ST_COMPLETED and next_state in completed_nstates:
        ej.state = next_state
        ej.output_data = output_data
        ej.save()

    else:
        raise EJobException("Wrong next_state")

    return ej

def ejob_cancel(job_id, owner_id):
    """get job and check if same owner

    transit to cancel state
    return True if success else EJobException is raised
    raise EJobException("error message")
    """
    ej = EJob.objects.get(Q(id__exact=job_id),Q(owner_id__exact=owner_id))

    st = ej.state
    if st in set([EJob.ST_SUBMITED, EJob.ST_STARTED]):
        ej.state = EJob.ST_CANCELLED
        ej.save()

    return ej

def ejob_get_gte_one(owner_id,worker_id,ejob_id=None):
    if ejob_id:
        return _remove_from_dict(EJob.objects.get(Q(id__exact=ejob_id),
                                              Q(owner_id__exact=owner_id) | Q(worker_id__exact=worker_id)), exclude=["_state"] )
    else:
        return [ _remove_from_dict(o,exclude=["_state"]) for o in EJob.objects.filter(Q(owner_id__exact=owner_id) | Q(worker_id__exact=worker_id)) ]

def _remove_from_dict(obj,exclude):
    """remove fields from obj"""
    d = copy.deepcopy(obj.__dict__)
    for el in exclude:
        del d[el]
    return d
