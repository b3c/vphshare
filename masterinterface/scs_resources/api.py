__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

import base64
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.models import User
from permissions.models import PrincipalRoleRelation, Role
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from masterinterface.atos.metadata_connector import filter_resources_by_facet, filter_resources_by_type, get_resource_metadata
from masterinterface.scs_resources.models import Resource, Workflow

Roles = ['Reader', 'Editor', 'Manager', 'Owner']
class has_local_roles(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, local_id='', type='', role='', ticket=''):
        """
            Process a search user request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            global_id (list): list of global id to check
            local_id (list) : list of local id to check
            type (string) : the type of the resource
            role (string) : the role to be checked
            ticket (string) : the authentication ticket - optional

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            client_address = request.META['REMOTE_ADDR']
            try:
                if request.GET.get('ticket'):
                    user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)
                else:
                    auth = request.META['HTTP_AUTHORIZATION'].split()
                    if len(auth) == 2:
                        if auth[0].lower() == 'basic':
                            # Currently, only basic http auth is used.
                            username, ticket = base64.b64decode(auth[1]).split(':')
                            user, tkt64 = authenticate(ticket=ticket, cip=client_address)
            except Exception, e:
                response = HttpResponse(status=401)
                response._is_string = True
                return response

            if user is not None:
                if request.GET.get('role','') not in Roles:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

                role = request.GET['role']

                # if global_id is provided, look for local resources
                if 'global_id' in request.GET:
                    global_ids = request.GET.getlist('global_id', [])
                    resources = []
                    for global_id in global_ids:
                        try:
                            resource = Resource.objects.get(global_id=global_id, metadata=False)
                        except ObjectDoesNotExist, e:
                            metadata = get_resource_metadata(global_id)
                            author = User.objects.get(username=metadata['author'])
                            if metadata['type'] == "Workflow":
                                resource, created = Workflow.objects.get_or_create(global_id=global_id, metadata=metadata, owner=author)
                                resource.save()
                                resource = resource.resource_ptr
                            else:
                                resource, created = Resource.objects.get_or_create(global_id=global_id, metadata=metadata, owner=author)
                                resource.save()

                        if resource.can_I(role, user):
                            resources.append(resource)
                        else:
                            return False

                    if len(resources) == 0:
                        # no resources with given ids!
                        response = HttpResponse(status=404)
                        response._is_string = True
                        return response

                    return True

                # if resource_type and local_ids are provided,
                else:
                    local_ids = request.GET.getlist('local_id', [])
                    resources = []
                    for local_id in local_ids:
                        r = filter_resources_by_facet(request.GET['type'], 'localID', local_id )
                        resources += r

                    if len(resources) == 0:
                        # no resources with given ids!
                        response = HttpResponse(status=404)
                        response._is_string = True
                        return response

                    for resource in resources:
                        try:
                            author = User.objects.get(username=resource['author'])
                            if resource['type'] == "Workflow":
                                resource_in_db, created = Workflow.objects.get_or_create(global_id=resource['globalID'], metadata=resource, owner=author)
                                resource_in_db.save()
                                resource_in_db = resource.resource_ptr
                            else:
                                resource_in_db, created = Resource.objects.get_or_create(global_id=resource['globalID'], metadata=resource, owner=author)
                                resource_in_db.save()

                            if not resource_in_db.can_I(role, user):
                                return False
                        except ObjectDoesNotExist, e:
                            # not in local db, no roles
                            return False

                    return True

            else:
                response = HttpResponse(status=403)
                response._is_string = True
                return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class get_resources_list(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, type='', role='', ticket=''):
        """
            Process a search user request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            type (string) : the type of the resource
            role (string) : the role to be checked
            ticket (string) : the authentication ticket - optional

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """

        try:
            client_address = request.META['REMOTE_ADDR']
            try:
                if request.GET.get('ticket'):
                    user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)
                else:
                    auth = request.META['HTTP_AUTHORIZATION'].split()
                    if len(auth) == 2:
                        if auth[0].lower() == 'basic':
                            # Currently, only basic http auth is used.
                            username, ticket = base64.b64decode(auth[1]).split(':')
                            user, tkt64 = authenticate(ticket=ticket, cip=client_address)
            except Exception, e:
                response = HttpResponse(status=401)
                response._is_string = True
                return response

            if user is not None:
                if request.GET('role','') not in Roles:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

                role = request.GET['role']
                if  request.GET.get('type', None) is not None:
                    resources = filter_resources_by_type(resource_type=request.GET['type'])
                    user_resources = []

                    for metadata in resources:
                        try:
                            try:
                                author = User.objects.get(username=metadata['author'])
                            except Exception, e:
                                continue
                            if metadata['type'] == "Workflow":
                                resource, created = Workflow.objects.get_or_create(global_id=metadata['globalID'], metadata=metadata, owner=author)
                                resource.save()
                                resource = resource.resource_ptr
                                resource.metadata = metadata
                            else:
                                resource, created = Resource.objects.get_or_create(global_id=metadata['globalID'], metadata=metadata, owner=author)
                                resource.save()

                            if resource.can_I(role,user):
                                user_resources.append(resource)

                        except ObjectDoesNotExist, e:
                            # not in local db, no roles
                            continue
                        return [{"local_id": r.metadata['localID'], "global_id": r.global_id} for r in user_resources]
                else:
                    user_resources = []
                    roles = Roles[Roles.index(Role.objects.get(role).name):]
                    role_relations = PrincipalRoleRelation.objects.filter(
                        Q(user=user) | Q(group__in=user.groups.all()),
                        role__name__in=roles,
                    )
                    for role_relation in role_relations:
                            if isinstance(role_relation.content, Resource) and role_relation.content not in user_resources:
                                user_resources.append(role_relation.content)

                    return [r.global_id for r in user_resources]
            else:
                response = HttpResponse(status=403)
                response._is_string = True
                return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response