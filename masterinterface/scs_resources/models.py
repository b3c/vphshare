from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from masterinterface.atos.metadata_connector import update_resource_metadata, get_resource_metadata
from config import request_accept_transition, resource_reader, ResourceWorkflow, ResourceRequestWorkflow, resource_owner
from workflows.utils import do_transition, set_workflow_for_model
from permissions.utils import add_local_role, add_role
from django.contrib.contenttypes.models import ContentType


class ResourceManager(models.Manager):

    def get(self, *args, **kwargs):
        resource = super(ResourceManager, self).get(*args, **kwargs)
        resource.metadata = get_resource_metadata(resource.global_id)
        return resource

    def all(self):
        resources = super(ResourceManager, self).all()
        for resource in resources:
            resource.metadata = get_resource_metadata(resource.global_id)
        return resources


class Resource(models.Model):

    global_id = models.CharField(null=True, max_length=39)
    owner = models.ForeignKey(User, default=1)

    # hack for security
    security_policy = models.CharField(verbose_name="Security Policy Name ", max_length=125, null=True, blank=True)
    security_configuration = models.CharField(verbose_name="Security Configuration Name ", max_length=125, null=True, blank=True)

    objects = ResourceManager()

    def save(self, force_insert=False, force_update=False, using=None, metadata={}):
        super(Resource, self).save(force_insert=force_insert, force_update=force_update, using=using)
        if self.__class__.__name__ == 'Resource':
            add_local_role(self, self.owner, resource_owner)
        else:
            # TODO this action should be performed only for workflows!
            # now it is ok since we have only Resource and Workflow
            update_resource_metadata(self.global_id, {'local_id': self.id, 'type': self.__class__.__name__})
            add_local_role(self.resource_ptr, self.owner, resource_owner)

    def __unicode__(self):
        return "%s" % self.global_id

    def update_views_counter(self):
        metadata = get_resource_metadata(self.global_id)
        try:
            views = int(metadata['views']) + 1
        except ValueError, e:
            views = 1
        update_resource_metadata(self.global_id, {'views': str(views)})
        return views


class ResourceRequest(models.Model):

    resource = models.ForeignKey(Resource)
    requestor = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.resource.id, self.requestor.username)

    def accept(self, initiator):
        if do_transition(self, request_accept_transition, initiator):
            # grant Reader role to the requestor
            add_local_role(self.resource, self.requestor, resource_reader)
            # TODO REMOVE HACK!
            add_role("%s_READER" % self.resource.global_id)


class Workflow(Resource):

    t2flow = models.FileField(verbose_name="Taverna workflow *", upload_to='./taverna_workflows/', help_text="Taverna workflow file, *.t2flow")
    xml = models.FileField(verbose_name="Input definition *", upload_to='./workflows_input/', help_text="Input definition file, *.xml")

    objects = ResourceManager()


# SET CONTENTYPE WORKFLOW
set_workflow_for_model(ContentType.objects.get_for_model(ResourceRequest), ResourceRequestWorkflow)
set_workflow_for_model(ContentType.objects.get_for_model(Resource), ResourceWorkflow)