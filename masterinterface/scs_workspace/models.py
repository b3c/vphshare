from django.db import models
from django.contrib.auth.models import User
from exceptions import WorkflowManagerException
from core import WorkflowManager


class TavernaExecutionManager(models.Manager):

    def get(self, *args, **kwargs):
        workflow_execution = super(TavernaExecutionManager, self).get(*args, **kwargs)
        workflow_execution.update()
        return workflow_execution

    def all(self):
        workflow_executions = super(TavernaExecutionManager, self).all()
        for workflow_execution in workflow_executions:
            workflow_execution.update()
        return workflow_executions


class TavernaExecution(models.Model):
    owner = models.ForeignKey(User)
    t2flow = models.FileField(verbose_name="Workflow Definition File", blank=True)
    baclava = models.FileField(verbose_name="Baclava Input definition", blank=True)
    title = models.CharField(max_length=120)
    workflowId = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=25, default="Initialized")

    def __unicode__(self):
        return "%s - %s (%s)" % (self.workflowId, self.status, self.owner.username)

    def submit(self, ticket):
        ret = WorkflowManager.submitWorkflow(self.title, self.t2flow, self.baclava, ticket)
        if 'workflowId' in ret and ret['workflowId']:
            self.workflowId = ret['workflowId']
        else:
            raise WorkflowManagerException(ret.get('error.code', ''), ret.get('error.description', ''))

    def update(self, info=[]):
        """ update workflow execution details information """
        if not info:
            try:
                self.info = WorkflowManager.getWorkflowInformation(self.workflowId)
                self.status = self.info['status']
            except Exception, e:
                raise WorkflowManagerException('500', 'Error while updating workflow %s' % self.workflowId)
        else:
            self.info = info
            self.status = self.info['status']

    def start(self):
        ret = WorkflowManager.startWorkflow(self.workflowId)
        if 'returnValue' in ret and ret['returnValue'] == 'ok':
            self.update()
            return True
        else:
            raise WorkflowManagerException(ret.get('error.code', ''), ret.get('error.description', ''))
