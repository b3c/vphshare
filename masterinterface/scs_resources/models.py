from django.db import models
from django.contrib.auth.models import User
from masterinterface.atos.metadata_connector import update_resource_metadata, get_resource_metadata, delete_resource_metadata
from config import request_accept_transition, resource_reader, ResourceWorkflow, ResourceRequestWorkflow, resource_owner
from workflows.utils import do_transition, set_workflow_for_model
from permissions.utils import add_local_role
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from permissions.models import PrincipalRoleRelation, Role
from django.db.models import ObjectDoesNotExist
from django.db.models import Q
from masterinterface.scs_groups.models import VPHShareSmartGroup
from django.db.models import Avg
from django.core.cache import cache
from django.conf import settings
from masterinterface.scs_resources.utils import get_resource_local_roles, get_resource_global_group_name, grant_permission, is_request_pending
import requests
import xmltodict

Roles = ['Reader', 'Editor', 'Manager', 'Owner']

def get_pending_requests_by_user(user):
    requests = ResourceRequest.objects.filter(resource__owner=user)
    pending_requests = []
    for r in requests:
        if is_request_pending(r):
            pending_requests.append(r)
    return pending_requests

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

    def solr_filter(self, rows=100, page=0, q=None, *args, **kwargs):
        #to check with Ivan if we can use the solr endpoint
        if q is None:
            q = " AND ".join('%s:"%s"' % (key,kwargs[key]) for key in kwargs.keys() if  not isinstance(kwargs[key], list))
            #query with inlusive list
            q2 = " AND ".join('%s:[%s]' % (key," ".join(str(value) for value in kwargs[key])) for key in kwargs.keys() if  isinstance(kwargs[key], list))
            if len(q2):
                q += " AND %s" % q2
        resources = []
        results = settings.MD_SEARCH_ENGINE.search(q, start=rows*page, rows=rows)
        for result in results:
            user = User.objects.filter(username=result['author'])
            if user.exists():
                #the results retunr by the search engine is a list with length one.
                result['type'] = result['type'][0]
                r, created = self.get_or_create(result["globalID"], metadata=result , owner=user[0])[0]
                if created:
                    r.save()
                resources.append(r)
        #resources = super(ResourceManager, self).filter(*args, **kwargs)
        return resources, results.hits


    def filter(self, *args, **kwargs):
        return super(ResourceManager, self).filter(*args, **kwargs)

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

    def load_permission(self):
        #method provide the load permission for specific types of resource : File and Dataset
        #load the permissions from the lobcder permissions map
        if 'File' in self.metadata['type']:
            permissions_match = {'read': 'Reader', 'write': 'Editor'}
            permissions_map = self.get_user_group_permissions_map()
            for permission in self.metadata['lobcderPermission']:
                if permission in permissions_match.keys():
                    role = Role.objects.get(name=permissions_match[permission])
                    for user_group in self.metadata['lobcderPermission'][permission]:
                        if user_group == 'vph':
                            #Mark as public the resrouce.
                            grant_permission(None, self, role)
                            continue
                        # check if the user/group in the lobcder permission list exisit in MI db.
                        if User.objects.filter(username=user_group).exists():
                            name = User.objects.get(username=user_group)
                        elif Group.objects.filter(name=user_group).exists():
                            name = Group.objects.get(name=user_group)
                        else:
                            name = None
                        # if user/group exsists and is not already seted the Manager permission I can grant the corresponding permission
                        if name and name in permissions_map and 'Manager' not in permissions_map[permissions_map.index(name)].roles:
                            grant_permission(user_group, self, role)
        # if is a Dataset method:
        if 'Dataset' in self.metadata['type']:
            for role in get_resource_local_roles():
                group_name = get_resource_global_group_name(self, role.name)
                try:
                    group, created = VPHShareSmartGroup.objects.get_or_create(name=group_name)
                    if created:
                        group.managers.add(self.owner)
                        group.user_set.add(self.owner)
                    add_local_role(self, group, role)
                except ObjectDoesNotExist, e:
                    pass

    def load_additional_metadata(self, ticket):
        #some information are built straing from teh exisitng metadata
        try:
            #1: File type need to query the lobcder to retrive the permissions schema, path and type(file or Folder)
            if 'File' in self.metadata['type']:
                    lobcder_item = requests.get('%s/item/query/%s' %(settings.LOBCDER_REST_URL, self.metadata['localID']),
                                                auth=('user', ticket),
                                                verify=False,
                                                headers={'Content-Type':'application/json','Accept':'application/json'}).json()
                    self.metadata['lobcderPath'] = lobcder_item['path']
                    self.metadata['lobcderPermission'] = lobcder_item['permissions']
                    self.metadata['lobcderPermission'].setdefault('read',[])
                    self.metadata['lobcderPermission'].setdefault('write',[])
                    self.metadata['lobcderPermission'].setdefault('owner',[])
                    self.metadata['fileType'] = lobcder_item['logicalData']['type'].split('.')[-1]
                    if self.metadata['fileType']:
                        self.metadata['format'] = self.metadata['name'].split('.')[-1]
                    else:
                        self.metadata['format'] = 'folder'
                    for permission, set in self.metadata['lobcderPermission'].items():
                        if not isinstance( set, list ):
                            self.metadata['lobcderPermission'][permission] = [ set ]
            #1: Dataset new version have the new sql/sparql endpoint to explore
            if 'Dataset' in self.metadata['type']:
                endpoint = self.metadata.get('sparqlEndpoint',self.metadata['localID'])
                if 'read/sparql' in endpoint:
                    self.metadata['explore'] = endpoint.replace('read/sparql', 'explore/sql.html')
                    self.metadata['explore'] = self.metadata['explore'].replace('https://','https://admin:%s@'%ticket)
            return True
        except Exception,e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            return False

    def load_full_metadata(self):
        # the resource returned by the search engine load the base schema type
        # special fields as realted resource  linked to semantic annotation are loader separatly from the raw
        if 'mrRaw' in self.metadata.keys():
            #metadata has loaded from solr so some fields are missing the basic schema.
            #TOUSE only if the metadata are loaded by solr
            self.metadata = xmltodict.parse(self.metadata['mrRaw'][0].encode('utf-8'))
        self.metadata['rating'] = float(self.metadata['rating'])
        if self.metadata.get('relatedResources',None) is not None and self.metadata.get('relatedResource',None) is not None:
            if  not isinstance(self.metadata['relatedResources']['relatedResource'], list):
                relatedResources = [self.metadata['relatedResources']['relatedResource'].copy()]
            else:
                relatedResources = self.metadata['relatedResources']['relatedResource'][:]
            self.metadata['relatedResources'] = []
            for global_id in relatedResources:
                r = Resource.objects.get(global_id=global_id['resourceID'])
                self.metadata['relatedResources'].append((global_id['resourceID'],r.metadata['name']))

        if self.metadata.get('linkedTo',None) is not None:
            if  not isinstance(self.metadata['linkedTo']['link'], list):
                self.metadata['linkedTo']['link'] = [self.metadata['linkedTo']['link'].copy()]
        if self.metadata.get('semanticAnnotations', None) is not None and self.metadata.get('semanticConcept', None) is not None:
            if  not isinstance(self.metadata['semanticAnnotations']['semanticConcept'], list):
                self.metadata['semanticAnnotations']['semanticConcept'] = [self.metadata['semanticAnnotations']['semanticConcept'].copy()]

    def reset_permissions(self):
        return PrincipalRoleRelation.objects.filter(role__name__in=['Reader', 'Editor', 'Manager'], content_id = self.id).delete()

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

    def get_pending_requests_by_resource(self):
        requests = ResourceRequest.objects.filter(resource=self)
        pending_requests = []
        for r in requests:
            if is_request_pending(r):
                pending_requests.append(r)
        return pending_requests

    def get_user_group_permissions_map(self):
        permissions_map = []

        ctype = ContentType.objects.get_for_model(self)
        # look for user with those roles
        role_relations = PrincipalRoleRelation.objects.filter(role__name__in=['Reader', 'Editor', 'Manager'], content_id=self.id, content_type=ctype)
        for r in role_relations:
            if r.user is not None and r.content_id == self.id:
                if r.user in permissions_map:
                    index = permissions_map.index(r.user)
                    if r.role.name not in permissions_map[index].roles:
                        permissions_map[index].roles.append(r.role.name)
                else:
                    if getattr(r.user, 'roles', None) is not None:
                        if r.role.name not in r.user.roles:
                            r.user.roles.append(r.role.name)
                    else:
                        r.user.roles = []
                        r.user.roles.append(r.role.name)
                    permissions_map.append(r.user)
            if r.group is not None and r.content_id == self.id:

                if self.metadata['type'] == 'Dataset':
                    ##Only for dataset maintain the Woody approach.
                    try:
                        vph_smart_group = VPHShareSmartGroup.objects.get(name=r.group.name)
                        for user in vph_smart_group.user_set.all():
                            if user in permissions_map:
                                index = permissions_map.index(user)
                                if r.role.name not in permissions_map[index].roles:
                                    permissions_map[index].roles.append(r.role.name)
                            else:
                                if getattr(user, 'roles', None) is None:
                                    user.roles = []
                                if r.role.name not in user.roles:
                                    user.roles.append(r.role.name)
                                permissions_map.append(user)
                    except Exception:
                        if r.group in permissions_map:
                            index = permissions_map.index(r.group)
                            if r.role.name not in permissions_map[index].roles:
                                permissions_map[index].roles.append(r.role.name)
                        else:
                            if getattr(r.group, 'roles', None) is not None:
                                if r.role.name not in r.group.roles:
                                    r.group.roles.append(r.role.name)
                            else:
                                r.group.roles = []
                                r.group.roles.append(r.role.name)
                            permissions_map.append(r.group)
                        pass
                    ##END - Only for dataset mantain the Woddy approch.
                else:
                    if r.group in permissions_map:
                        index = permissions_map.index(r.group)
                        if r.role.name not in permissions_map[index].roles:
                            permissions_map[index].roles.append(r.role.name)
                    else:
                        if getattr(r.group, 'roles', None) is not None:
                            if r.role.name not in r.group.roles:
                                r.group.roles.append(r.role.name)
                        else:
                            r.group.roles = []
                            r.group.roles.append(r.role.name)
                        permissions_map.append(r.group)
        #For Files and folder load the permission map directly from the lobcder.
        if self.metadata['type'] == 'File' and self.metadata.get('lobcderPermission', None) is not None:
            #get the user and groups available in my system to avoid conflict with lobcder custom users/groups not mappend in the MI.
            users_and_groups = set(self.metadata['lobcderPermission']['read']+self.metadata['lobcderPermission']['write']) - set(['vph'])
            from itertools import chain
            users_and_groups = chain(list(User.objects.filter(username__in=users_and_groups)) + list(Group.objects.filter(name__in=users_and_groups)))
            for user_group in users_and_groups:
                #if the user/group is Manager read and write are not loaded as Reader or
                #Editor permission except they already loaded before.
                if user_group in permissions_map:
                    index = permissions_map.index(user_group)
                    if 'Manager' not in permissions_map[index].roles:
                        #if the user is not Manager I load the permission as is.
                        name = getattr(user_group,'username',getattr(user_group,'name',None))
                        if name in self.metadata['lobcderPermission']['read'] and 'Reader' not in permissions_map[index].roles:
                            permissions_map[index].roles.append('Reader')
                        if name in self.metadata['lobcderPermission']['write'] and 'Editor' not in permissions_map[index].roles:
                            permissions_map[index].roles.append('Editor')
                else:
                    if getattr(user_group, 'roles', None) is None:
                        user_group.roles = []
                    name = getattr(user_group,'username',getattr(user_group,'name',None))
                    if name in self.metadata['lobcderPermission']['read'] and 'Reader' not in user_group.roles:
                        user_group.roles.append('Reader')
                    if name in self.metadata['lobcderPermission']['write'] and 'Editor' not in user_group.roles:
                        user_group.roles.append('Editor')
                    permissions_map.append(user_group)

        return permissions_map


    def can_I(self,role, user):
        roles = Roles[Roles.index(Role.objects.get(name=role).name):]
        role_relations = PrincipalRoleRelation.objects.filter(
            Q(user=user) | Q(group__in=user.groups.all()),
            role__name__in=roles,
            content_id=self.id
        )

        lobcder_permission = False
        if hasattr(self,'metadata') and  self.metadata.get('lobcderPermission', None):
            name = user.username
            if settings.DEBUG:
                name = role+"_dev"
            if role == "Reader":
                lobcder_permission = name in self.metadata['lobcderPermission']['read'] \
                    or user.groups.filter(name__in=self.metadata['lobcderPermission']['read']).exists()
            if role == "Editor":
                lobcder_permission = name in self.metadata['lobcderPermission']['write'] \
                    or user.groups.filter(name__in=self.metadata['lobcderPermission']['write']).exists()
            if role == "Manager":
                lobcder_permission = (name in self.metadata['lobcderPermission']['read'] or user.groups.filter(name__in=self.metadata['lobcderPermission']['read']).exists()) \
                    and (name in self.metadata['lobcderPermission']['write'] or user.groups.filter(name__in=self.metadata['lobcderPermission']['write']).exists())
            if role == "Owner":
                lobcder_permission = name in self.metadata['lobcderPermission']['owner'] \
                    or user.groups.filter(name__in=self.metadata['lobcderPermission']['owner']).exists()

        if role == 'Reader':
            read_all_relations = PrincipalRoleRelation.objects.filter(
            user=None, group=None,
            role__name__in=['Reader'],
            content_id=self.id
            )

            if role_relations.count() == 0 and read_all_relations.count() == 0 and not lobcder_permission:
                return False
        else:
            if role_relations.count() == 0 and not lobcder_permission:
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

            lobcder_permission = False
            if hasattr(self,'metadata') and  self.metadata.get('lobcderPermission', None):
                role = user.username
                if settings.DEBUG:
                    role = role+"_dev"
                lobcder_permission = role in self.metadata['lobcderPermission']['read'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['read']).exists() \
                                     or role in self.metadata['lobcderPermission']['owner'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['owner']).exists()

            if role_relations.count() == 0 and read_all_relations.count() == 0 and not lobcder_permission and not self.is_public():
                return False

            return True
        else:
            #for anonymous check if it is public.(is it a rigth behaivor)
            return False


    def can_edit(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Editor', 'Manager', 'Owner'],
                content_id=self.id
            )

            lobcder_permission = False
            if hasattr(self,'metadata') and self.metadata.get('lobcderPermission', None):
                role = user.username
                if settings.DEBUG:
                    role = role+"_dev"
                lobcder_permission = role in self.metadata['lobcderPermission']['write'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['write']).exists() \
                                     or role in self.metadata['lobcderPermission']['owner'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['owner']).exists()


            if role_relations.count() == 0 and not lobcder_permission:
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

            lobcder_permission = False
            if hasattr(self,'metadata') and self.metadata.get('lobcderPermission', None):
                role = user.username
                if settings.DEBUG:
                    role = role+"_dev"
                lobcder_permission = ((role in self.metadata['lobcderPermission']['read'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['read']).exists()) \
                                     and ((role in self.metadata['lobcderPermission']['write'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['write']).exists()))) \
                                     or role in self.metadata['lobcderPermission']['owner'] \
                                     or user.groups.filter(name__in=self.metadata['lobcderPermission']['owner']).exists()

            if role_relations.count() == 0 and not lobcder_permission:
                return False
            return True
        return False

    def is_public(self):
        read_all_relations = PrincipalRoleRelation.objects.filter(
            user=None, group=None,
            role__name__in=['Reader'],
            content_id=self.id
        )
        lobcder_permission = False
        if hasattr(self,'metadata') and self.metadata.get('lobcderPermission', None):
            role = 'vph'
            if settings.DEBUG:
                role = role+"_dev"
            lobcder_permission = role in self.metadata['lobcderPermission']['read']

        if read_all_relations.count() == 0 and not lobcder_permission:
            return False
        return True

    def is_owner(self, user):
        if not user.is_anonymous():
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=user) | Q(group__in=user.groups.all()),
                role__name__in=['Owner'],
                content_id=self.id
            )

            lobcder_permission = False
            if hasattr(self,'metadata') and  self.metadata.get('lobcderPermission', None):
                role = user.username
                if settings.DEBUG:
                    role = role+"_dev"
                lobcder_permission = role in self.metadata['lobcderPermission']['owner']

            if role_relations.count() == 0 and not lobcder_permission:
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

    def get_user_group_permissions_map(self):
        return self.resource_ptr.get_user_group_permissions_map()

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
