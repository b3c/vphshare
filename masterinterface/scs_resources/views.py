import json

from django.http import HttpResponse, Http404
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from workflows.utils import set_workflow, set_state, do_transition
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation, PermissionDenied

from masterinterface.scs_security.politicizer import create_policy_file
from masterinterface.cyfronet import cloudfacade
from .models import Resource, Workflow, ResourceRequest
from config import ResourceRequestWorkflow, request_accept_transition, request_refuse_transition
from forms import WorkflowForm, UsersGroupsForm, ResourceForm, SWSForm, DatasetForm
from masterinterface.atos.metadata_connector_json import *
from utils import *
from masterinterface import settings
from masterinterface.scs_resources.widgets import AdditionalFile, AdditionalLink

def resource_detailed_view(request, id='1'):
    """
        return the detailed view for a given resource
    """
    try:
        try:
            resource = Resource.objects.get(global_id=id)
        except ObjectDoesNotExist, e:
            metadata = get_resource_metadata(id)
            try:
                author = User.objects.get(username=metadata['author'])
            except ObjectDoesNotExist, e:
                #resource assigned to noone are ignored.
                raise  SuspiciousOperation
            if metadata['type'] == "Workflow":
                resource, created = Workflow.objects.get_or_create(global_id=id, metadata=metadata, owner=author, type=metadata['type'])
                resource.save()
                resource = resource.resource_ptr
            else:
                #some metadata File type are corrupted
                if metadata['type'] == "File" and metadata['localID'] == "0":
                    request.session['errormessage'] = "The File or folder you are looking for is corrupted.Err:No localID"
                    raise Exception
                resource, created = Resource.objects.get_or_create(global_id=id, metadata=metadata, owner=author, type=metadata['type'])
                resource.save()
        except MultipleObjectsReturned:

            # seems like the President has stolen something :-)
            resources = Resource.objects.filter(global_id=id)
            metadata = get_resource_metadata(global_id=id)
            for r in resources:
                if r.owner.username != metadata['author']:
                    r.delete()

            resource = Resource.objects.get(global_id=id)

            #assign metadata
            resource.metadata = metadata
        if resource.metadata['type'] == "File" and resource.metadata['localID'] == "0":
            request.session['errormessage'] = "The File or folder you are loking for is corrupted.Err:No localID"
            raise Exception

        #load the metadata to traslate in a more readable format.
        resource.load_full_metadata()

        if request.user.is_authenticated():
            resource.attach_permissions(user=request.user)
            resource.requests = resource.get_pending_requests_by_resource()
            resource.load_additional_metadata(request.ticket)
            resource.load_permission()
            try:
                resource_request = ResourceRequest.objects.get(resource=resource, requestor=request.user)
                resource_request_state = get_state(resource_request)
                if resource_request_state.name in ['Pending', 'Refused']:
                    resource.already_requested = True
                    resource.request_status = resource_request_state.name
            except ObjectDoesNotExist, e:
                resource.already_requested = False

        return render_to_response(
            'scs_resources/resource.html',
            {'resource': resource,
             'cloudFacadeUrl': settings.CLOUDFACACE_URL,
             'requests': []},
            RequestContext(request)
        )

    except SuspiciousOperation:
        raise SuspiciousOperation
    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        raise Http404

@login_required
def rate_resource(request, global_id, rate):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            if resource.can_read(request.user):
                resource.rate(request.user,rate)
            return HttpResponse(status=200)
        except Exception, e:
            return HttpResponse(status=500)
    return HttpResponse(status=500)


def request_for_sharing(request):
    """
        send a request for sharing to resource owner
    """

    resource = Resource.objects.get(id=request.GET.get('id'))
    relatedResources = request.GET.getlist('relatedResources', [])
    resource_request, created = ResourceRequest.objects.get_or_create(resource=resource, requestor=request.user)
    resource_request.message = request.GET.get('message', None)
    resource_request.save()

    set_workflow(resource_request, ResourceRequestWorkflow)
    set_state(resource_request, request_pending)

    # alert owner by email
    try:
        alert_user_by_email(
            mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
            mail_to='%s %s <%s>' % (resource.owner.first_name, resource.owner.last_name, resource.owner.email),
            subject='[VPH-Share] You have receive a request for sharing',
            mail_template='incoming_request_for_sharing',
            dictionary={
                'message': request.GET.get('message', None),
                'resource': resource,
                'requestor': request.user,
                'BASE_URL': settings.BASE_URL
            }
        )

        # alert requestor by email
        alert_user_by_email(
            mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
            mail_to='%s %s <%s>' % (request.user.first_name, request.user.last_name, request.user.email),
            mail_template='request_for_sharing_sent',
            subject='[VPH-Share] Your request for sharing has been delivered to resource owner',
            dictionary={
                'requestor': request.user
            }
        )
    except Exception, e:
        pass

    for related in relatedResources:
        resource = Resource.objects.get(global_id=related)
        resource_request, created = ResourceRequest.objects.get_or_create(resource=resource, requestor=request.user)
        resource_request.message = request.GET.get('message', None)
        resource_request.save()

        set_workflow(resource_request, ResourceRequestWorkflow)
        set_state(resource_request, request_pending)

        # alert owner by email
        try:
            alert_user_by_email(
                mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                mail_to='%s %s <%s>' % (resource.owner.first_name, resource.owner.last_name, resource.owner.email),
                subject='[VPH-Share] You have receive a request for sharing',
                mail_template='incoming_request_for_sharing',
                dictionary={
                    'message': request.GET.get('message', None),
                    'resource': resource,
                    'requestor': request.user,
                    'BASE_URL': settings.BASE_URL
                }
            )

            # alert requestor by email
            alert_user_by_email(
                mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                mail_to='%s %s <%s>' % (request.user.first_name, request.user.last_name, request.user.email),
                mail_template='request_for_sharing_sent',
                subject='[VPH-Share] Your request for sharing has been delivered to resource owner',
                dictionary={
                    'requestor': request.user
                }
            )
        except Exception, e:
            pass

    # return to requestor
    response_body = json.dumps({"status": "OK", "message": "The Resource owner has received your request."})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response

def resources(request,tab='Dataset'):

    search_text = request.GET.get('search_text', '')
    types = request.GET.get('types', [])
    if type(types) in (str, unicode):
        types = types.split(',')[:-1]
    filterby = [tab]
    if type(filterby) in (str, unicode):
        filterby = filterby.split(',')[:-1]
    categories = request.GET.get('categories', [])
    if type(categories) in (str, unicode):
        categories = categories.split(',')[:-1]
    authors = request.GET.get('authors', [])
    if type(authors) in (str, unicode):
        authors = authors.split(',')[:-1]
    licences = request.GET.get('licences', [])
    if type(licences) in (str, unicode):
        licences = licences.split(',')[:-1]
    tags = request.GET.get('tags', [])
    if type(tags) in (str, unicode):
        tags = tags.split(',')[:-1]

    search = {
        'search_text': search_text,
        'type': types,
        'categories': categories,
        'authors': authors,
        'licences': licences,
        'tags': tags,
        'filterby': filterby
    }

    return render_to_response("scs_resources/resources.html",
                              {'search': search, "results":None, "numResults": 0, 'countType': {}, 'filterToshow':'true',
                              'types': ['Dataset', 'Workflow', 'AtomicService', 'File', 'SemanticWebService'] , 'tab': tab, 'user':''},
                              RequestContext(request))


def get_resources_list(request, resource_type):

    search_text = request.GET.get('search_text', '')
    types = request.GET.get('types', [])
    if type(types) in (str, unicode):
        types = types.split(',')[:-1]
    filterby = [resource_type]
    if type(filterby) in (str, unicode):
        filterby = filterby.split(',')[:-1]
    categories = request.GET.get('categories', [])
    if type(categories) in (str, unicode):
        categories = categories.split(',')[:-1]
    authors = request.GET.get('authors', [])
    if type(authors) in (str, unicode):
        authors = authors.split(',')[:-1]
    licences = request.GET.get('licences', [])
    if type(licences) in (str, unicode):
        licences = licences.split(',')[:-1]
    tags = request.GET.get('tags', [])
    if type(tags) in (str, unicode):
        tags = tags.split(',')[:-1]

    search = {
        'search_text': search_text,
        'type': types,
        'categories': categories,
        'authors': authors,
        'licences': licences,
        'tags': tags,
        'filterby': filterby
    }

    return render_to_response("scs_resources/resource_list.html",
                              {'search': search, "results":None, "numResults": 0, 'countType': {}, 'filterToshow':'true',
                              'types': ['Dataset', 'Workflow', 'AtomicService', 'File', 'SemanticWebService']},
                              RequestContext(request))


@login_required
def manage_resources(request, tab='Dataset'):
    if request.user.is_authenticated():
        search_text = request.GET.get('search_text', '')
        types = request.GET.get('types', [])
        if type(types) in (str, unicode):
            types = types.split(',')[:-1]
        filterby = [tab]
        if type(filterby) in (str, unicode):
            filterby = filterby.split(',')[:-1]
        categories = request.GET.get('categories', [])
        if type(categories) in (str, unicode):
            categories = categories.split(',')[:-1]
        authors = request.GET.get('authors', [])
        if type(authors) in (str, unicode):
            authors = authors.split(',')[:-1]
        licences = request.GET.get('licences', [])
        if type(licences) in (str, unicode):
            licences = licences.split(',')[:-1]
        tags = request.GET.get('tags', [])
        if type(tags) in (str, unicode):
            tags = tags.split(',')[:-1]

        search = {
            'search_text': search_text,
            'type': types,
            'categories': categories,
            'authors': authors,
            'licences': licences,
            'tags': tags,
            'filterby': filterby
        }

        return render_to_response("scs_resources/manage_resources.html",
                                  {'search': search, "results":None, "numResults": 0, 'countType': {}, 'filterToshow':'true',
                                  'types': ['Dataset', 'Workflow', 'AtomicService', 'File', 'SemanticWebService'] , 'tab': tab, 'user':request.user.username},
                                  RequestContext(request))
    else:
        raise PermissionDenied

@login_required
def get_resources_list_by_author(request, resource_type, page=1):
    if request.method == 'GET':
        try:
            #get the list of owned resource from the metadata repository
            if resource_type == "data":
                resources = Resource.objects.filter_by_roles('Reader', User.objects.get(username='asagli'), types='Dataset', public=False, page=page)
                types= ['Dataset']
            if resource_type == "file":
                resources = Resource.objects.filter_by_roles('Reader',User.objects.get(username='asagli'), types='File', public=False, page=page)
                types= ['File']
            if resource_type == "application":
                resources = Resource.objects.filter_by_roles('Reader',User.objects.get(username='asagli'), types='AtomicService', public=False, page=page)
                types= ['AtomicService']
            if resource_type == "workflow":
                resources = Workflow.objects.filter_by_roles('Reader',User.objects.get(username='asagli'), types='Workflow', public=False, page=page)
                types= ['Workflow']
            if resource_type == "sws":
                resources = Resource.objects.filter_by_roles('Reader',User.objects.get(username='asagli'), types='SemanticWebService', public=False, page=page)
                types= ['SemanticWebService']

            for resource in resources['data']:
                if resource.metadata['type'] == "File" and resource.metadata['localID'] == "0":
                    continue
                if 'File' in types and resource.metadata['type'] == 'File':
                    #load additional metadata and permission from LOBCDER services
                    if not resource.load_additional_metadata(request.ticket):
                        #if something go wrong with the lobcder loader I skip it
                        continue
                resource.load_permission()
                #load requests pending for this resource
                resource.requests = resource.get_pending_requests_by_resource()

            resultsRender = render_to_string("scs_resources/resource_list.html", {"resources": resources,"types":types, "type":resource_type, 'user':request.user, 'page':page, 'request':request})
            del(resources['resource_metadata'])
            del(resources['data'])
            return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender, 'info':resources}, sort_keys=False),
                            content_type='application/json')
        except Exception, e:
            return HttpResponse(status=500)


def get_resources_details(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            resource.requests = resource.get_pending_requests_by_resource()
            if hasattr(request,'ticket'):
                resultsRender = render_to_string("scs_resources/resource_details.html", {"resource": resource, 'user':request.user, 'ticket':request.ticket})
            else:
                resultsRender = render_to_string("scs_resources/resource_details.html", {"resource": resource, 'user':request.user, 'ticket':''})
            return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender}, sort_keys=False),
                            content_type='application/json')
        except Exception, e:
            return HttpResponse(status=500)

@login_required
def get_resources_share(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            #get the path information using the lobcder services.
            if resource.metadata['type'] == 'File':
                #load additional metadata and permission from LOBCDER services
                resource.load_additional_metadata(request.ticket)
            resource.load_permission()

            resource.roleslist = get_resource_local_roles(resource)
            resource.requests = resource.get_pending_requests_by_resource()
            resource.sharreduser = resource.get_user_group_permissions_map()
            resource.user_group_finder = UsersGroupsForm(id="user_group_"+resource.global_id,
                                                         excludedList=resource.sharreduser + [request.user] )
            from django.core.context_processors import csrf
            context = {"resource": resource, 'user':request.user}
            context.update(csrf(request))
            resultsRender = render_to_string("scs_resources/resource_security.html", context)
            return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender}, sort_keys=False),
                            content_type='application/json')
        except Exception, e:
            return HttpResponse(status=500)

def publish_resource(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            update_resource_metadata(global_id, {'status':'Active'}, resource.metadata['type'])
            cache.delete(global_id)
            return HttpResponse(status=200)
        except Exception, e:
            return HttpResponse(status=500)
    return HttpResponse(status=500)

def unpublish_resource(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            update_resource_metadata(global_id, {'status':'Inactive'}, resource.metadata['type'])
            cache.delete(global_id)
            return HttpResponse(status=200)
        except Exception, e:
            return HttpResponse(status=500)
    return HttpResponse(status=500)

def mark_resource_public(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            role = Role.objects.get(name='Reader')
            grant_permission(None,resource,role,request.ticket)
            #add_local_role(resource, None, role)
            return HttpResponse(status=200)
        except Exception, e:
            return HttpResponse(status=500)
    return HttpResponse(status=500)

def mark_resource_private(request, global_id):
    if request.method == 'GET':
        try:
            resource = Resource.objects.get(global_id=global_id)
            role = Role.objects.get(name='Reader')
            revoke_permision(None,resource,role,request.ticket)
            return HttpResponse(status=200)
        except Exception, e:
            return HttpResponse(status=500)
    return HttpResponse(status=500)

def acceptRequest(request):
    if request.method == 'POST':
        name = request.POST.get('user')
        role = Role.objects.get(name=request.POST.get('role'))
        resource = Resource.objects.get(global_id=request.POST.get('resource'))

        principal = grant_permission(name, resource, role, request.ticket)

        # change request state if exists
        try:
            resource_request = ResourceRequest.objects.filter(requestor=principal, resource=resource)
            if resource_request.count() and is_request_pending(resource_request[0]):
                do_transition(resource_request[0], request_accept_transition, request.user)
                resource_request[0].delete()

                # alert requestor
                alert_user_by_email(
                    mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                    mail_to='%s %s <%s>' % (principal.first_name, principal.last_name, principal.email),
                    subject='[VPH-Share] Your request for sharing has been accepted',
                    mail_template='request_for_sharing_accepted',
                    dictionary={
                        'resource': resource,
                        'requestor': principal,
                        'BASE_URL': settings.BASE_URL
                    }
                )
        except Exception, e:
            pass

        request.session['collapse'] = [resource.global_id]
        return redirect(reverse('manage-data') + "#" + str(resource.id))
    return HttpResponse(status="500")


def rejectRequest(request):
    if request.method == 'POST':
        name = request.POST.get('user')
        resource = Resource.objects.get(global_id=request.POST.get('resource'))
        principal = User.objects.get(username=name)
        # change request state if exists
        try:
            resource_request = ResourceRequest.objects.filter(requestor=principal, resource=resource)
            if resource_request.count() and is_request_pending(resource_request[0]):
                do_transition(resource_request[0], request_refuse_transition, request.user)
                resource_request[0].delete()
                # alert requestor
                alert_user_by_email(
                    mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                    mail_to='%s %s <%s>' % (principal.first_name, principal.last_name, principal.email),
                    subject='[VPH-Share] Your request for sharing has been refused',
                    mail_template='request_for_sharing_refused',
                    dictionary={
                        'resource': resource,
                        'requestor': principal,
                        'message': request.POST.get('message')
                    }
                )
        except Exception, e:
            pass

        request.session['collapse'] = [resource.global_id]
        return redirect(reverse('manage-data') + "#" + str(resource.id))
    return HttpResponse(status="500")


def newshare(request):
    if request.method == 'POST':
        input = request.POST.getlist('Usersinput')
        resource = Resource.objects.get(global_id=request.POST.get('resource'))
        roles = []
        if request.POST.get('editor', None):
            roles.append(request.POST.get('editor', None))
        if request.POST.get('reader', None):
            roles.append(request.POST.get('reader', None))
        if request.POST.get('manager', None):
            roles.append(request.POST.get('manager', None))
        if len(roles) > 0:
            for usergroup in input:
                splitted = usergroup.split('_')[0]
                name = usergroup.replace(splitted + '_', '')
                for role in roles:
                    role = Role.objects.get(name=role)
                    principal = grant_permission(name, resource, role, request.ticket)
                    try:
                        resource_request = ResourceRequest.objects.filter(requestor=principal, resource=resource)
                        if resource_request.count() and is_request_pending(resource_request[0]):
                            do_transition(resource_request[0], request_accept_transition, request.user)
                            resource_request[0].delete()

                            # alert requestor
                            alert_user_by_email(
                                mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                                mail_to='%s %s <%s>' % (principal.first_name, principal.last_name, principal.email),
                                subject='[VPH-Share] New resource shared with you',
                                mail_template='new_share',
                                dictionary={
                                    'resource': resource,
                                    'requestor': principal
                                }
                            )
                    except Exception, e:
                        pass
            request.session['collapse'] = [resource.global_id]
            return redirect(reverse('manage-data') + "#" + str(resource.id))
    return HttpResponse(status="500")


def grant_role(request):
    """
        grant role to user or group
    """

    # if has_permission(request.user, "Manage sharing"):
    name = request.GET.get('name')
    role = Role.objects.get(name=request.GET.get('role'))
    resource = Resource.objects.get(global_id=request.GET.get('global_id'))

    principal = grant_permission(name, resource, role, request.ticket)

    # change request state if exists
    try:
        resource_request = ResourceRequest.objects.filter(requestor=principal, resource=resource)
        if resource_request.count() and is_request_pending(resource_request[0]):
            do_transition(resource_request[0], request_accept_transition, request.user)
            resource_request[0].delete()

            # alert requestor
            alert_user_by_email(
                mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
                mail_to='%s %s <%s>' % (principal.first_name, principal.last_name, principal.email),
                subject='[VPH-Share] Your request for sharing has been accepted',
                mail_template='request_for_sharing_accepted',
                dictionary={
                    'message': request.GET.get('requestmessage', ''),
                    'resource': resource,
                    'requestor': principal
                }
            )

    except ObjectDoesNotExist, e:
        pass
    except Exception, e:
        pass

    response_body = json.dumps({"status": "OK", "message": "Role granted correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response

@login_required
def grant_recursive_role(request):
    """
        grant role to user or group recursively only for folders
    """

    resource = Resource.objects.get(global_id=request.GET.get('global_id'))
    resource.load_additional_metadata(request.ticket)
    if resource.metadata['fileType'] == 'folder':
        data = requests.get('%s/item/permissions/%s' %(settings.LOBCDER_REST_URL, resource.metadata['localID']),
                                                    auth=('user', request.ticket),
                                                    verify=False,
                                                    headers={'Content-Type':'application/json','Accept':'application/json'}).text
        result =  requests.put('%s/item/permissions/recursive/%s?getall=True' % (settings.LOBCDER_REST_URL, resource.metadata['localID']),
                                                    auth=('user', request.ticket),
                                                    verify=False,
                                                    headers={'Content-Type':'application/json','Accept':'application/json'},
                                                    data=data)
        if result.status_code not in [204,201,200]:
                raise Exception('LOBCDER permision set error')
        resoources_guid_applied = result.json()
        permissions_map = resource.get_user_group_permissions_map()
        # if the recurive operation changed other Files or Folder permission I need to reset mine permission map
        #and reload to maintain coherence
        if 'guid' in resoources_guid_applied.keys():
            #load all the paermissions maps where the new map has applied.
            if isinstance(resoources_guid_applied['guid'], list):
                for guid in resoources_guid_applied['guid']:
                    try:
                        r = Resource.objects.get(global_id=guid)
                    except ObjectDoesNotExist:
                        continue
                    r.reset_permissions()
                    for user_group in permissions_map:
                        for role_name in user_group.roles:
                            role = Role.objects.get(name=role_name)
                            name = getattr(user_group,'username',getattr(user_group,'name',None))
                            grant_permission(name,r,role)
            else:
                try:
                    r = Resource.objects.get(global_id=resoources_guid_applied['guid'])
                    r.reset_permissions()
                    for user_group in permissions_map:
                        for role_name in user_group.roles:
                            role = Role.objects.get(name=role_name)
                            name = getattr(user_group,'username',getattr(user_group,'name',None))
                            grant_permission(name,r,role)
                except ObjectDoesNotExist:
                    pass
    else:
        raise SuspiciousOperation

    response_body = json.dumps({"status": "OK", "message": "Role granted correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response


def revoke_role(request):
    """
        revoke role from user or group
    """

    # if has_permission(request.user, "Manage sharing"):
    name = request.GET.get('name')
    role = Role.objects.get(name=request.GET.get('role'))
    resource = Resource.objects.get(global_id=request.GET.get('global_id'))

    revoke_permision(name,resource,role,request.ticket)

    response_body = json.dumps({"status": "OK", "message": "Role revoked correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response

# I don't know why but nobody use this view TOFIX!
def create_role(request):
    """
        create the requested role and the relative security
    """

    # if has_permission(request.user, "Create new role"):
    role_name = request.GET.get('role')
    role, created = Role.objects.get_or_create(name=role_name)
    if not created:
        # role with that name already exists
        response_body = json.dumps({"status": "KO", "message": "Role with name %s already exists" % role_name, "alertclass": "alert-error"})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response

    policy_file = create_policy_file(['read'], [role_name])
    if cloudfacade.create_securitypolicy(request.user.username, request.ticket, role_name, policy_file):
        response_body = json.dumps({"status": "OK", "message": "Role created correctly", "alertclass": "alert-success", "rolename": role_name})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response
    else:
        response_body = json.dumps({"status": "KO", "message": "Interaction with security agent failed", "alertclass": "alert-error"})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response


def workflowsView(request):

    workflows = []

    return render_to_response("scs_resources/workflows.html", {'workflows': workflows}, RequestContext(request))

@login_required
def edit_resource(request, id=False):

    try:

        global_id=id
        dbResource = None
        edit = True
        if global_id:
            dbResource = Resource.objects.get(global_id=global_id)
            if dbResource.metadata['type'] == "Workflow":
                dbResource = Workflow.objects.get(global_id=global_id)
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=request.user) | Q(group__in=request.user.groups.all()),
                role__name__in=['Editor','Manager','Owner'],
                content_id=dbResource.id
            )

            if role_relations.count() == 0:
                return render_to_response('scs/no_permission.html',
                    context_instance=RequestContext(request)
                )

        if request.method == "GET":
            if id:
                dbResource.load_additional_metadata(request.ticket)
                dbResource.metadata['title'] = dbResource.metadata['name']
                if dbResource.metadata['type'] == "Workflow":
                    form = WorkflowForm(dbResource.metadata, instance=dbResource)
                elif dbResource.metadata['type'] == "SemanticWebService":
                    form = SWSForm(dbResource.metadata, instance=dbResource)
                elif dbResource.metadata['type'] == "Dataset":
                    form = DatasetForm(dbResource.metadata, instance=dbResource)
                else:
                    form = ResourceForm(dbResource.metadata, instance=dbResource)
            else:
                #the workflow create request
                form = WorkflowForm()
                return render_to_response("scs_resources/edit_resources.html",
                                  {'form':form, 'edit':False,'type':'Workflow'},
                                  RequestContext(request))

        if request.method == "POST":
            if dbResource is None:
                request.POST.update({'author':request.user.username, 'localID':'','type':'Workflow'})
                form = WorkflowForm(request.POST, request.FILES)
                edit = False
                if form.is_valid():
                    resource = form.save(commit=False, owner=request.user)
                    resource.save()
                    request.session['statusmessage'] = 'Workflow created'
                    return redirect('/resources/%s' % resource.global_id)
            elif dbResource.metadata['type'] == "Workflow":
                form = WorkflowForm(request.POST, request.FILES, instance=dbResource)
            elif dbResource.metadata['type'] == "SemanticWebService":
                form = SWSForm(request.POST, request.FILES, instance=dbResource)
            elif dbResource.metadata['type'] == "Dataset":
                form = DatasetForm(request.POST, request.FILES, instance=dbResource)
            else:
                form = ResourceForm(request.POST, request.FILES, instance=dbResource)

            if form.is_valid():
                resource = form.save(commit=False, owner=dbResource.owner)
                resource.save()
                request.session['statusmessage'] = 'Changes were successful'
                return redirect('/resources/%s' % resource.global_id)
        if dbResource:
            type_request = dbResource.metadata['type']
        else:
            type_request = 'Workflow'
        return render_to_response("scs_resources/edit_resources.html",
                                  {'form':form, 'edit':edit,'type':type_request},
                                  RequestContext(request))
    except AtosServiceException, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        if dbResource:
            type_request = dbResource.metadata['type']
        else:
            type_request = 'Workflow'
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_resources/edit_resources.html",
                  {'form':form, 'edit':edit,'type':type_request},
                  RequestContext(request))

    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        if not request.session.get('errormessage', False):
            request.session['errormessage'] = 'Some errors occurs, please try later. '
        return redirect('/resources/%s' % global_id)

@login_required
def edit_workflow(request, id=False):
    try:
        if id:
            dbWorkflow = Workflow.objects.get(id=id)
            role_relations = PrincipalRoleRelation.objects.filter(
                Q(user=request.user) | Q(group__in=request.user.groups.all()),
                role__name__in=['Editor','Manager','Owner'],
                content_id=dbWorkflow.resource_ptr.id
            )

            if role_relations.count() == 0:
                return render_to_response('scs/no_permission.html',
                    context_instance=RequestContext(request)
                )

            dbWorkflow.metadata['title'] = dbWorkflow.metadata['name']
            form = WorkflowForm(dbWorkflow.metadata, instance=dbWorkflow)

        if request.method == "POST":
            form = WorkflowForm(request.POST, request.FILES, instance=dbWorkflow)

            if form.is_valid():
                workflow = form.save(commit=False, owner=dbWorkflow.owner)
                workflow.save()
                request.session['statusmessage'] = 'Changes were successful'
                return redirect('/workflows')

        return render_to_response("scs_resources/workflows.html",
                                  {'form':form, 'edit':True},
                                  RequestContext(request))
    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_resources/workflows.html",
                                  {},
                                  RequestContext(request))

    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        if not request.session.get('errormessage', False):
            request.session['errormessage'] = 'Some errors occurs, please try later. '
        return redirect('/workflows')



@login_required
def create_workflow(request):
    try:
        form = WorkflowForm()
        if request.method == 'POST':
            form = WorkflowForm(request.POST, request.FILES)

            if form.is_valid():
                form.save(owner=request.user)
                request.session['statusmessage'] = 'Workflow successfully created'
                return redirect('/workflows')
            else:
                request.session['errormessage'] = 'Some fields are wrong or missed.'
                return render_to_response("scs_resources/workflows.html", {'form': form,  'edit':False}, RequestContext(request))
        raise

    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_resources/workflows.html", {'form': form}, RequestContext(request))

    except Exception, e:
        return render_to_response("scs_resources/workflows.html", {'form': form}, RequestContext(request))


def api_help(request):
    return render_to_response(
        'scs_resources/api.html',
        RequestContext(request)
    )

@csrf_exempt
def add_file_to_form(request):
    if request.POST.get('key', None):
        new_file = AdditionalFile()
        return HttpResponse(content=new_file.render(request.POST.get('key', None),None))
    return HttpResponse(status=403)

@csrf_exempt
def add_link_to_form(request):
    if request.POST.get('key', None):
        new_link = AdditionalLink()
        return HttpResponse(content=new_link.render(request.POST.get('key', None),None))
    return HttpResponse(status=403)


def smart_get_AS(request):
    if request.GET.get('term',None):
        results = filter_resources_by_facet('AtomicService', 'name', request.GET.get('term',None))
        response = []
        for result in results['resource_metadata']:
            result = result.value
            response.append((result['globalID'], result['name']))
    else:
        response = []
    from django_select2.views import Select2View
    res = Select2View()
    return res.render_to_response(res._results_to_context(('nil', False, response)))

def smart_get_SWS(request):
    if request.GET.get('term',None):
        results = filter_resources_by_facet('SemanticWebService', 'name', request.GET.get('term',None))
        response = []
        for result in results['resource_metadata']:
            result = result.value
            response.append((result['globalID'], result['name']))
    else:
        response = []
    from django_select2.views import Select2View
    res = Select2View()
    return res.render_to_response(res._results_to_context(('nil', False, response)))

def smart_get_resources(request):
    if request.GET.get('term',None):
        results = filter_resources_by_facet('GenericMetadata', 'name', request.GET.get('term',None))
        response = []
        for result in results['resource_metadata']:
            result = result.value
            response.append((result['globalID'], result['name']))
    else:
        response = []
    from django_select2.views import Select2View
    res = Select2View()
    return res.render_to_response(res._results_to_context(('nil', False, response)))

#1000 <----------------------------------------------------------------------------------------

def discoveries(request,tab=''): 
    return render_to_response(
        "scs_resources/discoveries.html", 
        {
         'tab':tab
        },
        RequestContext(request)
    )


def globalsearch(request):
    if request.method == 'GET':
        try:
            #get the list of owned resource from the metadata repository
            page = int(request.GET['start'])/int(request.GET['length']) + 1
            columns = ['type', 'name', 'author', 'updateDate', 'rating', 'views']
            search_text = request.GET.get('request[search_text]', '*')
            user = request.GET.get('request[dashboard]', '')
            types = request.GET.get('types', [])
            if type(types) in (str, unicode):
                types = types.split(',')[:-1]
            filterby = request.GET.getlist('request[filterby][]', [])
            if type(filterby) in (str, unicode):
                filterby = filterby.split(',')[:-1]
            categories = request.GET.getlist('request[categories][]', [])
            if type(categories) in (str, unicode):
                categories = categories.split(',')[:-1]
            authors = request.GET.getlist('request[authors][]', [])
            if type(authors) in (str, unicode):
                authors = authors.split(',')[:-1]
            licences = request.GET.getlist('request[licences][]', [])
            if type(licences) in (str, unicode):
                licences = licences.split(',')[:-1]
            tags = request.GET.getlist('request[tags][]', [])
            if type(tags) in (str, unicode):
                tags = tags.split(',')[:-1]

            expression = {
                'type': [] if 'all' in filterby else filterby,
                'category': categories,
                'author': authors,
                'licence': licences,
                'tags': tags
            }

            if not request.user.is_authenticated() and user !='':
                raise PermissionDenied
            elif request.user.is_authenticated() and user !='' and request.user.username != user:
                return PermissionDenied
            elif request.user.is_authenticated() and request.user.username == user:
                response = Resource.objects.filter_by_roles(role='Reader',user=request.user,types=filterby[0],public=False,page= page, orderBy=columns[int(request.GET.get('order[0][column]'))], orderType=request.GET.get('order[0][dir]'),numResults=int(request.GET['length']), search_text=search_text, expression=expression)
                resources = response['data']
            elif request.session.get('institutionportal', None) is not None:
                group=request.session['institutionportal'].institution.group_ptr
                types = None if 'all' in filterby or filterby == [] else filterby[0]
                response = Resource.objects.filter_by_roles(role='Reader',types=types, group=group,public=False,page= page, orderBy=columns[int(request.GET.get('order[0][column]'))], orderType=request.GET.get('order[0][dir]'),numResults=int(request.GET['length']), search_text=search_text, expression=expression)
                resources = response['data']
            else:
                response = search_resource(search_text,expression, numResults=int(request.GET['length']), page= page, orderBy=columns[int(request.GET.get('order[0][column]'))], orderType=request.GET.get('order[0][dir]'))
                resources = response['resource_metadata']


            results = {
              "draw":0,
              "recordsTotal": response['numTotalMetadata'],
              "recordsFiltered": response['numTotalMetadata'],
              "data": [],
              "DT_RowClass":[]
            }
            for resource in resources:
                if hasattr(resource, 'metadata'):
                    resource = resource.metadata
                else:
                    resource = resource.value
                    #create the resrouce entry in my db if it doesn't exisit
                    u, usercreated = User.objects.get_or_create(username=resource['author'])
                    if resource['type'] == 'Workflow':
                        r, created = Workflow.objects.get_or_create(global_id=resource['globalID'], metadata = resource)
                    else:
                        r, created = Resource.objects.get_or_create(global_id=resource['globalID'], metadata = resource)
                    if created:
                        r.owner = u
                        r.type = resource['type']
                        r.save()

                results['data'].append({
                    'type':'<i title="%s" class="fa fa-%s"></i>'%( resource['type'], resource['type']),
                    'name':str(resource.get('name','')),
                    'owner':resource['author'],
                    'update': str( resource.get('updateDate', '') ),
                    'rating':resource['rating'],
                    'views':resource['views'],
                    'actions':{'global_id':resource['globalID'], 'name':resource['name']},
                    'DT_RowClass': resource['type']+'-light-bkgr',
                })

            del(response['resource_metadata'])
            if response.get('data',None):
                del(response['data'])
            results['info'] = response
            return HttpResponse(status=200,
                            content=json.dumps(results, sort_keys=False),
                            content_type='application/json')
        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            raise SuspiciousOperation( str(e) )

def resource_modal(request, global_id):
    r = Resource.objects.get(global_id=global_id)
    if request.user.is_authenticated():
        r.load_additional_metadata(request.ticket)
        r.load_permission()
        r.attach_pemissions(user=request.user)
        return render_to_response("scs_resources/resource_modal.html",{'resource':r},RequestContext(request))
    else:
        r.attach_pemissions()

    return render_to_response("scs_resources/resource_modal.html",{'resource':r},RequestContext(request))

def get_discoveries_list(request, resource_type=None, page=1):
    if request.method == 'GET':
        try:
            if resource_type == 'all':
                resource_type = None
            if request.session.get('institutionportal', None) is None:
                raise Exception("no institutionportal defined")
            #get the list of owned resource from the metadata repository
            resources = Resource.objects.filter_by_roles('Reader',types=resource_type, group=request.session['institutionportal'].institution.group_ptr,public=False,page=page)
            resultsRender = render_to_string("scs_resources/discoveries_list.html", {"resources": resources,  'user':request.user, 'page':page})

            del(resources['data'])
            del(resources['resource_metadata'])

            return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender, 'info':resources}, sort_keys=False),
                            content_type='application/json')
        except Exception, e:
            return HttpResponse(status=500)


#1000 <----------------------------------------------------------------------------------------

