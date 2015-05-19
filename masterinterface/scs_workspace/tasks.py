from __future__ import absolute_import

from celery import shared_task
from .core import WorkflowManager
from masterinterface.scs.models import Notification
from masterinterface.scs_workspace.models import TavernaExecution
from django.conf import settings
from django.contrib.auth.models import User
import base64
import time


@shared_task
def execute_workflow(ticket, execution_id, title, taverna_atomic_id, t2flow, baclava, url=''):
    """
    Provide a method to call the workflow manager and wait that the execution is completed.
    Arguments:
        ticket (string): The ticket of the user that start the execution
        execution_id: The corresponding primary key present in Taverna execution model
        title: The title provided by the user
        taverna_atomic_id: Atomic service ID in the cloud
        t2flow : Taverna workflow definition (string),
        baclava : Input Definition (string)
        url (optional) : The taverna url rest api in the form http://host/taverna-server/rest/runs
                         if it is set by the user the taverna_atomic_id is ignored.
    Return:
        Success : 'True' The execution is end without problem , call get_execution_infos() to have all the informations
        Fail : 'False' Something went wrong during the execution, call get_execution_infos() to have all the informations

    """
    try:
        user_data = settings.TICKET.validateTkt(base64.b64decode(ticket))
        # The task have the submition workaround activated.##
        ret = WorkflowManager.execute_workflow(ticket, execution_id, title, taverna_atomic_id, t2flow, baclava, url, True)
        if ret:
            ret = WorkflowManager.getWorkflowInformation(execution_id, ticket)
            while ret != False and (ret.get('executionstatus', -1) < 8 and ret.get('error', False) != True):
                ret = WorkflowManager.getWorkflowInformation(execution_id, ticket)
            if user_data:
                try:
                    user = User.objects.get(username = user_data[2][0])
                    subject = "Workflow execution is completed"
                    message = '%s is completed, click %s/workspace/#%s to see the results.' % (title, settings.BASE_URL, execution_id)
                    Notification(recipient=user, message=message, subject=subject).save()
                except Exception, e:
                    #problem with email notification. Ignored.(only for local instance)
                    pass
        return True
    except Exception, e:        
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        return False


@shared_task
def get_execution_infos(execution_id, ticket):
    """
    It is the tak responsable of the updating of taverna execution informations get by the WM
    Arguments:
        execution_id: The corresponding primary key present in Taverna execution model
        ticket: The user that had requested the execution
    Return:
        Success: The execution is end and all the informations are stored in the database.
        Fail : False , It mean that the execution is not started yet, or the execution id requested not exist.
    """
    try:
        ret = {}
        taverna_execution = TavernaExecution.objects.get(pk=execution_id, ticket=ticket)
        keys = ['executionstatus', 'error', 'error_msg', 'workflowId', 'endpoint', 'asConfigId', 'createTime', 'expiry', 'startTime', 'Finished', 'exitcode', 'stdout', 'stderr', 'outputfolder']
        # Update the database every 5 seconds until user delete the execution or the execution is end.
        while not(taverna_execution is None and ret == False) and (ret.get('executionstatus', -1) < 8 and ret.get('error', False) != True):
            ret_new = WorkflowManager.getWorkflowInformation(execution_id, ticket)
            taverna_execution = TavernaExecution.objects.get(pk=execution_id, ticket=ticket)
            if ret_new != ret and type(ret_new) is not bool:
                ret = ret_new
                for key in keys:
                    setattr(taverna_execution,key,ret_new.get(key, ''))
                taverna_execution.save()
            time.sleep(5)
        ret_new = WorkflowManager.getWorkflowInformation(execution_id, ticket)
        taverna_execution = TavernaExecution.objects.get(pk=execution_id, ticket=ticket)
        for key in keys:
            setattr(taverna_execution,key,ret_new.get(key, ''))
        taverna_execution.task_id = None
        taverna_execution.status = 'Completed'
        taverna_execution.save()
        WorkflowManager.deleteExecution(taverna_execution.id, ticket)
        # Add notification when it finished
        user_data = settings.TICKET.validateTkt(base64.b64decode(ticket))
        if user_data:
            try:
                user = User.objects.get(username = user_data[2][0])
                subject = "Workflow execution is completed"
                message = '%s is completed, click <a href="%s/workspace/#%s">here</a> to see the results.' % (taverna_execution.title, settings.BASE_URL, execution_id)
                Notification(recipient=user, message=message, subject=subject).save()
            except Exception, e:
                #problem with email notification. Ignored.
                pass
        return True
    except Exception, e :
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        return False


