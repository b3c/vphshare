__author__ = 'Matteo Balasso <m.balasso@scsitaly.com>'

import json
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from piston.handler import BaseHandler
from permissions.utils import add_local_role
from masterinterface.scs_auth.auth import authenticate
from models import VPHShareSmartGroup, InstitutionPortal
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
                        Q(username__icontains=term) | Q(email__icontains=term) | Q(first_name__icontains=term) | Q(
                            last_name__icontains=term)
                    )

                    return [{"username": user.username, "fullname": "%s %s" % (user.first_name, user.last_name),
                             "email": user.email} for user in users]

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class search_userandgroup(BaseHandler):
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

                    groups = Group.objects.filter(name__icontains=term)

                    return {
                        "users": [{"username": user.username, "fullname": "%s %s" % (user.first_name, user.last_name)} for user in users],
                        "groups": [{"groupname": g.name, "subscribers": len(g.user_set.all())} for g in groups],
                    }

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
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

                    return [{"groupname": g.name, "subscribers": len(g.user_set.all())} for g in groups]

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


def can_be_child(child, parent):
    if str(child.name).lower() == str(parent.name).lower():
        return False

    if parent.parent:
        return can_be_child(child, parent.parent.vphsharesmartgroup)

    return True


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

                    name = request.GET.get('group')

                    # check if a user with the group name exists
                    try:
                        User.objects.get(username__iexact=name) #select case-insensitive
                        response = HttpResponse(status=500)
                        response._is_string = True
                        return response

                    except ObjectDoesNotExist, e:
                        pass

                    try:
                        Group.objects.get(name__iexact=name)    #select case-insensitive
                        response = HttpResponse(status=500)
                        response._is_string = True
                        return response

                    except ObjectDoesNotExist, e:
                        pass

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

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
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

                    name = request.GET.get('group')

                    group = VPHShareSmartGroup.objects.get(name=name)

                    if not user in group.managers.all():
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                    group.active = False
                    group.remove_users()
                    # remove this group from children parent reference
                    for child in VPHShareSmartGroup.objects.filter(parent=group):
                        child.parent = None
                        child.save()
                    group.parent = None
                    group.save()

                    response = HttpResponse(status=200)
                    response._is_string = True
                    response.write("OK")
                    return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


def add_user_to_group(user, group):
    group.user_set.add(user)
    for child in VPHShareSmartGroup.objects.filter(parent=group):
        add_user_to_group(user, child)


class add_to_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', name=''):
        """
            Add a user to a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name
            name (string) : the username or the group name to add

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))

                    if not group.is_manager(user):
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                    try:
                        user_to_add = User.objects.get(username=request.GET.get('name'))
                        # add user to all children groups
                        if request.GET.get('recursive', False):
                            add_user_to_group(user_to_add, group)
                        else:
                            group.user_set.add(user_to_add)

                    except ObjectDoesNotExist, e:
                        try:
                            group_to_add = VPHShareSmartGroup.objects.get(name=request.GET.get('name'))
                            if not can_be_child(group_to_add, group):
                                response = HttpResponse(status=500, content="constraint violation circularity")
                                response._is_string = True
                                return response
                            group_to_add.parent = group
                            group_to_add.save()
                        except ObjectDoesNotExist, e:
                            response = HttpResponse(status=403)
                            response._is_string = True
                            return response

                    response = HttpResponse(status=200)
                    response._is_string = True
                    response.write("OK")
                    return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class remove_user_from_group(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', username='', recursive=False):
        """
            Remove a user from a smart group
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            group (string) : the group name
            username (string) : the username
            recursive (string) : if present the user will be removed from all the tree of group

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                    user_to_remove = User.objects.get(username=request.GET.get('username'))

                    if not group.is_manager(user):
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                    if request.GET.get('recursive', False):
                        # remove user from all sub groups
                        while group is not None:
                            group.user_set.remove(user_to_remove)
                            try:
                                group = VPHShareSmartGroup.objects.get(parent=group)
                            except ObjectDoesNotExist, e:
                                group = None

                    else:
                        # remove only from this group
                        group.user_set.remove(user_to_remove)

                    response = HttpResponse(status=200)
                    response._is_string = True
                    response.write("OK")
                    return response

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class group_members(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group=''):
        """
            Given a group name, return the list of subscribers
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

                    try:
                        group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                    except ObjectDoesNotExist, e:
                        response = HttpResponse(status=404)
                        response._is_string = True
                        return response

                    return {
                        "users": [{"username": user.username, "fullname": "%s %s" % (user.first_name, user.last_name),
                                   "email": user.email} for user in group.user_set.all()],
                        "groups": [{"groupname": g.name, "subscribers": len(g.user_set.all())} for g in
                                   VPHShareSmartGroup.objects.filter(parent=group)]
                    }

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class user_groups(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', username=''):
        """
            Given a username, return the list of groups he is part of
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.
            username(string) : the username you want to know the groups

            Return:

            Successes - Json/xml/yaml format response
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:

                    try:
                        target_user = User.objects.get(username=request.GET.get('username'))
                    except ObjectDoesNotExist, e:
                        response = HttpResponse(status=404)
                        response._is_string = True
                        return response
                    if request.GET.get('institution', None) is None:
                        res = [{"groupname": g.name, "subscribers": len(g.user_set.all())} for g in
                            target_user.groups.all()]
                    else:
                        res = [{"groupname": g.institution.name, "subscribers": len(g.institution.user_set.all())} for g in
                           InstitutionPortal.objects.all() if target_user in g.institution.user_set.all()]
                    return res

                else:
                    response = HttpResponse(status=403)
                    response._is_string = True
                    return response

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class promote_user(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', username=''):
        """
            Promote a user as manager of a group
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

                    group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                    user_to_promote = User.objects.get(username=request.GET.get('username'))

                    if not group.is_manager(user):
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                    # add user to the managers
                    group.managers.add(user_to_promote)

                    # add user to the group and all sub groups
                    while group is not None:
                        group.user_set.add(user_to_promote)
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

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response


class downgrade_user(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket='', group='', username=''):
        """
            Promote a user as manager of a group
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

                    group = VPHShareSmartGroup.objects.get(name=request.GET.get('group'))
                    user_to_downgrade = User.objects.get(username=request.GET.get('username'))

                    if not group.is_manager(user):
                        response = HttpResponse(status=403)
                        response._is_string = True
                        return response

                    # remove user from the group managers and all sub groups
                    while group is not None:
                        # group.user_set.remove(user_to_downgrade)
                        group.managers.remove(user_to_downgrade)
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

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True
            return response