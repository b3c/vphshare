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

    def filter(self,*args, **kwargs):
        workflow_executions = super(TavernaExecutionManager, self).filter(*args, **kwargs)
        for workflow_execution in workflow_executions:
            workflow_execution.update()
        return workflow_executions


class TavernaExecution(models.Model):
    owner = models.ForeignKey(User)
    t2flow = models.TextField(verbose_name="Workflow Definition File Content", blank=True)
    baclava = models.TextField(verbose_name="Baclava Input Definition File Content", blank=True)
    title = models.CharField(max_length=120, verbose_name="Workflow Execution Title", help_text="Insert a meaningful name for this execution")
    workflowId = models.CharField(max_length=80, blank=True)
    taverna_id = models.CharField(max_length=80, blank=True)
    as_config_id = models.CharField(max_length=80, blank=True)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=80, default="Initialized")

    objects = TavernaExecutionManager()

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
        return None
        if not info:
            try:
                self.info = WorkflowManager.getWorkflowInformation(self.workflowId)
                if self.info['status'] == "unknown run UUID":
                    WorkflowManager.deleteWorkflow(self.workflowId)
                    WorkflowManager.deleteTavernaServerWorkflow(self.workflowId, user, ticket)
                    self.delete()
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

    def isReady(self):
        return self.status != 'Created'
