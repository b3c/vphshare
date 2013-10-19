from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from masterinterface.scs_resources.models import Workflow
from exceptions import WorkflowManagerException
from core import wfmng


class WorkflowExecutionManager(models.Manager):

    def get(self, *args, **kwargs):
        workflow_execution = super(WorkflowExecutionManager, self).get(*args, **kwargs)
        workflow_execution.update()
        return workflow_execution

    def all(self):
        workflow_executions = super(WorkflowExecutionManager, self).all()
        for workflow_execution in workflow_executions:
            workflow_execution.update()
        return workflow_executions


class WorkflowExecution(models.Model):
    owner = models,ForeignKey(User)
    t2flow = models.FileField(verbose_name="Workflow Definition File", blank=True)
    baclava = models.FileField(verbose_name="Baclava Input definition", blank=True)
    title = models.CharField(max_length=120)
    workflowId = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=25, default="Initialized")

    def __unicode__(self):
        return "%s - %s (%s)" % (self.workflowId, self.status, self.owner.username)

    def submit(self, ticket):
        ret = wfmng.submitWorkflow(self.title, self.workflow.t2flow, self.baclava, ticket)
        if 'workflowId' in ret and ret['workflowId']:
            self.workflowId = ret['workflowId']
        else:
            raise WorkflowManagerException(ret.get('error.code', ''), ret.get('error.description', ''))

    def update(self, info=[]):
        """ update workflow execution details information """
        if not info:
            try:
                self.info = wfmng.getWorkflowInformation(workflow_execution.workflowId)
                self.status = self.info['status']
            except Exception, e:
                raise WorkflowManagerException(ret.get('error.code', ''), ret.get('error.description', ''))
        else:
            self.info = info
            self.status = self.info['status']

    def start(self):
        ret = wfmng.startWorkflow(self.workflowId)
        if 'returnValue' in ret and ret['returnValue'] == 'ok':
            self.update()
            return True
        else:
            raise WorkflowManagerException(ret.get('error.code', ''), ret.get('error.description', ''))

    def isFinished(self):
        """ return true if the workflow is finished """
        if self.status == 'Finished':
            return True
        return False

    def isReady(self):
        """ return True if the workflow is ready to be started """
        if self.status == 'Initialized':
            return True
        return False

    def isRunning(self):
        """ return True if the workflow is running """
        if self.status == 'Operating':
            return True
        return False

