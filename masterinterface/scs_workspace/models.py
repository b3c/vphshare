from django.db import models
from django.contrib.auth.models import User
from core import WorkflowManager
from celery import group

class TavernaExecutionManager(models.Manager):

    def get(self, ticket, *args, **kwargs):
        workflow_execution = super(TavernaExecutionManager, self).get(*args, **kwargs)
        workflow_execution.update(ticket)
        return workflow_execution

    def all(self, ticket):
        workflow_executions = super(TavernaExecutionManager, self).all()
        for workflow_execution in workflow_executions:
            workflow_execution.update(ticket)
        return workflow_executions

    def filter(self, ticket, *args, **kwargs):
        workflow_executions = super(TavernaExecutionManager, self).filter(*args, **kwargs)
        for workflow_execution in workflow_executions:
            workflow_execution.update(ticket)
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
    taverna_atomic_id = models.CharField(max_length=80, blank=True)
    task_id = models.CharField(max_length=80, blank=True, null=True, default=None)
    creation_datetime = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    #info get by workflowmnager and updated authomaticaly during the workflow execution.
    #executionstatus = models.IntegerField(blank=True, null=True)
    #error = models.CharField(max_length=10, blank=True)
    #error_msg = models.CharField(max_length=120, blank=True)
    #endpoint = models.CharField(max_length=600, blank=True)
    #asConfigId = models.CharField(max_length=80, blank=True)
    #expiry = models.CharField(max_length=80, blank=True)
    #startTime = models.CharField(max_length=80, blank=True)
    #Finished = models.CharField(max_length=10, blank=True)
    #exitcode = models.CharField(max_length=10, blank=True)
    #stdout = models.TextField(blank=True)
    #stderr = models.TextField(blank=True)
    #outputfolder = models.CharField(max_length=600, blank=True)

    objects = TavernaExecutionManager()

    def __unicode__(self):
        return "%s - %s (%s)" % (self.workflowId, self.status, self.owner.username)

    def start(self, ticket):
        from masterinterface.scs_workspace import tasks
        self.status = 'Started'
        self.save()
        task = tasks.execute_workflow.delay(ticket, self.id, self.title, self.taverna_atomic_id, self.t2flow, self.baclava, self.url)
        self.task_id = task.id
        self.save()

    def update(self, ticket):
        keys = ['executionstatus', 'error', 'error_msg', 'workflowId', 'endpoint', 'asConfigId', 'createTime', 'expiry', 'startTime', 'Finished', 'exitcode', 'stdout', 'stderr', 'outputfolder']
        ret = WorkflowManager.getWorkflowInformation(self.id, ticket)
        if ret != False:
            for key in keys:
                setattr(self, key, ret.get(key, ''))
        else:
            ret = [0, False, '', '', self.url, '', '', '', '', '', '', '', '', '']
            for i in range(0, len(keys)):
                setattr(self, keys[i], ret[i])

    def delete(self, ticket, *args, **kwargs):
        try:
            WorkflowManager.deleteExecution(self.id, ticket)
        except Exception, e:
            pass
        super(TavernaExecution, self).delete(*args, **kwargs)
        return True

    def is_ready(self):
        return self.executionstatus == 0 and self.status != 'Started'

    def is_running(self):
        return self.status == 'Started' and self.executionstatus >= 0 and self.executionstatus < 8

    def is_completed(self):
        return self.status != 'Completed'