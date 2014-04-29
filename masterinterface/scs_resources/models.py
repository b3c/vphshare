from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from masterinterface.atos.metadata_connector import update_resource_metadata, get_resource_metadata, delete_resource_metadata
from config import request_accept_transition, resource_reader, ResourceWorkflow, ResourceRequestWorkflow, resource_owner
from workflows.utils import do_transition, set_workflow_for_model
from permissions.utils import add_local_role, add_role
from django.contrib.contenttypes.models import ContentType
from permissions.models import PrincipalRoleRelation, Role
from django.db.models import Q
from masterinterface.scs_groups.models import VPHShareSmartGroup
from django.http import QueryDict
from django.db.models import Avg
from django.core.cache import cache

Roles = ['Reader', 'Editor', 'Manager', 'Owner']

class ResourceManager(models.Manager):

    def get_or_create(self, global_id, metadata = [], **kwargs):
        resource, create = super(ResourceManager, self).get_or_create(global_id=global_id, **kwargs)
        if cache.get(resource.global_id) is None and metadata:
            cache.set(resource.global_id, metadata, 120)
        resource.metadata = metadata
        return resource, create


    def get(self,metadata=True, *args, **kwargs):
        resource = super(ResourceManager, self).get(*args, **kwargs)
        if metadata:
            if cache.get(resource.global_id) is None:
                resource.metadata = get_resource_metadata(resource.global_id)
                cache.set(resource.global_id, resource.metadata, 120)
            else:
                resource.metadata = cache.get(resource.global_id)
        return resource

    def all(self, metadata=False):
        resources = super(ResourceManager, self).all()
        if metadata:
            for resource in resources:
                if cache.get(resource.global_id) is None:
                    resource.metadata = get_resource_metadata(resource.global_id)
                    cache.set(resource.global_id, resource.metadata, 120)
                else:
                    resource.metadata = cache.get(resource.global_id)
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
            update_resource_metadata(self.global_id, {'localID': self.id, 'type': self.__class__.__name__},self.__class__.__name__ )
            add_local_role(self.resource_ptr, self.owner, resource_owner)

    def __unicode__(self):
        return "%s" % self.global_id

    def update_views_counter(self):
        metadata = get_resource_metadata(self.global_id)
        try:
            views = int(metadata['views']) + 1
        except ValueError, e:
            views = 1
        update_resource_metadata(self.global_id, {'views': str(views)}, metadata['type'])
        return views

    def delete(self, using=None, delete_metadata = False):
        if delete_metadata:
            delete_resource_metadata(self.global_id)
        return super(Resource, self).delete(using)

    def can_I(self,role, user):
        roles = Roles[Roles.index(Role.objects.get(name=role).name):]
        role_relations = PrincipalRoleRelation.objects.filter(
            Q(user=user) | Q(group__in=user.groups.all()),
            role__name__in=roles,
            content_id=self.id
        )
        if role == 'Reader':
            read_all_relations = PrincipalRoleRelation.objects.filter(
            user=None, group=None,
            role__name__in=['Reader'],
            content_id=self.id
            )

            if role_relations.count() == 0 and read_all_relations.count() == 0:            
                return False
        else:
            if role_relations.count() == 0:
                return False
        return True

    def can_read(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Reader', 'Editor', 'Manager', 'Owner'],
                content_id=self.id
            )

            read_all_relations = PrincipalRoleRelation.objects.filter(
                user=None, group=None,
                role__name__in=['Reader'],
                content_id=self.id
            )

            if role_relations.count() == 0 and read_all_relations.count() == 0:
                return False

            return True
        else:
            read_all_relations = PrincipalRoleRelation.objects.filter(
                user=None, group=None,
                role__name__in=['Reader'],
                content_id=self.id
            )

            if read_all_relations.count() == 0:
                return False

            return True


    def can_edit(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Editor', 'Manager', 'Owner'],
                content_id=self.id
            )

            if role_relations.count() == 0:
                return False
            return True
        return False

    def can_manage(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Manager', 'Owner'],
                content_id=self.id
            )

            if role_relations.count() == 0:
                return False
            return True
        return False

    def is_public(self):
        read_all_relations = PrincipalRoleRelation.objects.filter(
            user=None, group=None,
            role__name__in=['Reader'],
            content_id=self.id
        )

        if read_all_relations.count() == 0:
            return False
        return True

    def is_owner(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Owner'],
                content_id=self.id
            )

            if role_relations.count() == 0:
                return False
            return True
        return False

    def is_active(self):
        return bool(self.metadata['status'] in ['active', 'Active'])

    def rate(self, user, rating):
        if Rating.objects.filter(user=user, resource=self).count() > 0:
            Rating.objects.filter(user=user, resource=self).delete()
        Rating.objects.create(rate=rating, user=user, resource=self)
        avg = Rating.objects.filter(resource=self).aggregate(Avg('rate'))['rate__avg']
        update_resource_metadata(self.global_id, {'globalID':self.metadata['globalID'], 'rating': str(avg), 'type': self.metadata['type']}, self.metadata['type'])
        cache.delete(self.global_id)
        return True


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
            #add_role("%s_READER" % self.resource.global_id)


class Workflow(Resource):

    t2flow = models.FileField(verbose_name="Taverna workflow *", upload_to='./taverna_workflows/', help_text="Taverna workflow file, *.t2flow")
    xml = models.FileField(verbose_name="Input definition *", upload_to='./workflows_input/', help_text="Input definition file, *.xml")

    objects = ResourceManager()

    def can_I(self,role, user):
        return self.resource_ptr.can_I(role, user)

    def can_read(self, user):
        return self.resource_ptr.can_read(user)

    def can_edit(self, user):
        return self.resource_ptr.can_edit(user)

    def can_manage(self, user):
        return self.resource_ptr.can_manage(user)

    def is_public(self):
        return self.resource_ptr.is_public()

    def is_owner(self, user):
        return self.resource_ptr.is_owner(user)

    def rate(self, user, rating):
        return self.resource_ptr.rate(user, rating)

# SET CONTENTYPE WORKFLOW
set_workflow_for_model(ContentType.objects.get_for_model(ResourceRequest), ResourceRequestWorkflow)
set_workflow_for_model(ContentType.objects.get_for_model(Resource), ResourceWorkflow)

class Rating(models.Model):
    rate = models.IntegerField(blank=False, null=False)
    resource = models.ForeignKey(Resource)
    user = models.ForeignKey(User)
