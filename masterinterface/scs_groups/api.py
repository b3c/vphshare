__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

import json
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from piston.handler import BaseHandler
from permissions.utils import add_local_role
from masterinterface.scs_auth.auth import authenticate
from models import VPHShareSmartGroup
from config import group_manager


class search_user(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', term=''):
        """
            Process a search user request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            term (string) : search term

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    term = request.GET.get('term', '')

                    users = User.objects.filter(
                        Q(username__icontains=term) | Q(email__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term)
                    )

                    return [user.username for user in users]

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class search_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', term=''):
        """
            Process a search group request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            term (string) : search term

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    term = request.GET.get('term', '')

                    groups = Group.objects.filter(name__icontains=term)

                    return [group.name for group in groups]

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class create_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', name='', parent=''):
        """
            Create a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name
            parent (string): the parent group name (optional)

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    if user.is_staff:
                        # temporary constraint

                        name = request.GET.get('group')
                        parent = request.GET.get('parent', '')

                        group = VPHShareSmartGroup.objects.create(name=name)
                        group.managers.add(user)
                        group.user_set.add(user)
                        add_local_role(group, user, group_manager)

                        if parent:
                            try:
                                group.parent = Group.objects.get(name=parent)
                            except ObjectDoesNotExist, e:
                                pass

                        group.save()

                        response = HttpResponse(status=200)
                        response._is_string = True
                        response.write("OK")
                        return response

                    else:
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class delete_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', name=''):
        """
            Delete a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    if user.is_staff:
                        # temporary constraint

                        name = request.GET.get('group')

                        group = VPHShareSmartGroup.objects.get(name=name)

                        if not user in group.managers.all():
                            response = HttpResponse(status=403)
                            response._is_string = True
                            return response

                        group.active = False
                        group.remove_users()
                        group.save()

                        response = HttpResponse(status=200)
                        response._is_string = True
                        response.write("OK")
                        return response

                    else:
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class add_user_to_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', username=''):
        """
            Add a user to a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name
            username (string) : the username

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    if user.is_staff:
                        # temporary constraint

                        group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                        user_to_add = User.objects.get(username=request.GET.get('username'))

                        if not user in group.managers.all():
                            response = HttpResponse(status=403)
                            response._is_string = True
                            return response

                        group.user_set.add(user_to_add)
                        # add user to all parent group
                        while group.parent is not None:
                            group = VPHShareSmartGroup.objects.get(name=group.parent.name)
                            group.user_set.add(user_to_add)

                        response = HttpResponse(status=200)
                        response._is_string = True
                        response.write("OK")
                        return response

                    else:
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class remove_user_from_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', username=''):
        """
            Remove a user from a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name
            username (string) : the username

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    if user.is_staff:
                        # temporary constraint

                        group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                        user_to_remove = User.objects.get(username=request.GET.get('username'))

                        if not user in group.managers.all():
                            response = HttpResponse(status=403)
                            response._is_string = True
                            return response

                        # remove user from all sub groups
                        while group is not None:
                            group.user_set.remove(user_to_remove)
                            try:
                                group = VPHShareSmartGroup.objects.get(parent=group)
                            except ObjectDoesNotExist, e:
                                group = None

                        response = HttpResponse(status=200)
                        response._is_string = True
                        response.write("OK")
                        return response

                    else:
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            response = HttpResponse(status=500)
            response._is_string = True
            return response