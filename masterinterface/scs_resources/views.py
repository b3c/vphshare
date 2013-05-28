
# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.db.models import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from permissions.models import PrincipalRoleRelation, Role
from permissions.utils import add_role, remove_role, has_local_role, has_permission, add_local_role, remove_local_role
from workflows.utils import get_state, set_workflow, set_state, do_transition
import json
from masterinterface.scs_security.politicizer import create_policy_file, extract_permission_map
from masterinterface.scs_security.configurationizer import create_configuration_file, extract_configurations
from masterinterface.cyfronet import cloudfacade
from masterinterface.atos.metadata_connector import get_resource_metadata, AtosServiceException
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Resource, Workflow, ResourceRequest
from config import ResourceRequestWorkflow, request_pending, request_accept_transition
from forms import WorkflowForm
from masterinterface.atos.metadata_connector import *
from utils import get_permissions_map, get_pending_requests_by_resource, is_request_pending


def alert_user_by_email(mail_from, mail_to, subject, mail_template, dictionary={}):
    """
        send an email to alert user
    """

    text_content = loader.render_to_string('scs_resources/%s.txt' % mail_template, dictionary=dictionary)
    html_content = loader.render_to_string('scs_resources/%s.html' % mail_template, dictionary=dictionary)
    msg = EmailMultiAlternatives(subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.content_subtype = "html"
    msg.send()


def resource_detailed_view(request, id='1'):
    """
        return the detailed view for a given resource
    """

    try:
        resource = Resource.objects.get(global_id=id)
    except ObjectDoesNotExist, e:
        # create into local database the resource
        metadata = get_resource_metadata(id)
        # look for resource owner, if he exists locally
        try:
            resource_owner = User.objects.get(username=metadata['author'])
            # TODO create a particular type of resource rather than a Resource
            if str(metadata['type']).lower() == "workflow":
                resource = Workflow(global_id=id, owner=resource_owner)
            else:
                resource = Resource(global_id=id, owner=resource_owner)
            resource.save(metadata=metadata)

        except ObjectDoesNotExist, e:
            # TODO create a new user or assign resource temporarly to the President :-)
            resource = Resource(global_id=id, owner=User.objects.get(username='mbalasso'))
            resource.save(metadata=metadata)

        finally:
            resource.metadata = metadata

    # Count visit hit
    resource.metadata['views'] = resource.update_views_counter()

    # INJECT DEFAULT VALUES
    resource.citations = [{'citation': "STH2013 VPH-Share Dataset CVBRU 2011", "link": "doi:12.34567/891011.0004.23"}]
    resource.status = "Published"
    resource.language = "English"
    resource.version = "1.0"
    resource.related = []

    # check if the resource has been already requested by user
    if not request.user.is_anonymous(): # and not has_permission(resource, request.user, 'can_read_resource'):
        try:
            resource_request = ResourceRequest.objects.get(resource=resource, requestor=request.user)
            resource_request_state = get_state(resource_request)
            if resource_request_state.name in ['Pending', 'Refused']:
                resource.already_requested = True
                resource.request_status = resource_request_state.name
        except ObjectDoesNotExist, e:
            resource.already_requested = False

    try:
        workflow = Workflow.objects.get(global_id=id)
    except ObjectDoesNotExist, e:
        workflow = None

    return render_to_response(
        'scs_resources/resource_details.html',
        {'resource': resource,
         'workflow': workflow,
         'requests': []},
        RequestContext(request)
    )


def request_for_sharing(request):
    """
        send a request for sharing to resource owner
    """

    resource = Resource.objects.get(id=request.GET.get('id'))
    resource_request, created = ResourceRequest.objects.get_or_create(resource=resource, requestor=request.user)
    resource_request.save()

    # TODO these actions should be not necessary
    # Check int the models package
    # set_workflow_for_model(ContentType.objects.get_for_model(ResourceRequest), ResourceRequestWorkflow)
    set_workflow(resource_request, ResourceRequestWorkflow)
    set_state(resource_request, request_pending)

    # alert owner by email
    alert_user_by_email(
        mail_from='VPH-Share Webmaster <webmaster@vph-share.eu>',
        mail_to='%s %s <%s>' % (resource.owner.first_name, resource.owner.last_name, resource.owner.email),
        subject='[VPH-Share] You have receive a request for sharing',
        mail_template='incoming_request_for_sharing',
        dictionary={
            'message': request.GET.get('requestmessage', ''),
            'resource': resource,
            'requestor': request.user
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

    # return to requestor
    response_body = json.dumps({"status": "OK", "message": "The Resource owner has received your request."})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response


@login_required
def manage_resources(request):

    workflows = []
    datas = []
    applications = []

    try:
        db_workflows = Workflow.objects.all()
        for workflow in db_workflows:
            resource = workflow.resource_ptr

            if has_local_role(request.user, 'Owner', resource) or has_local_role(request.user, 'Manager', resource):
                workflow.permissions_map = get_permissions_map(resource)
                workflow.requests = get_pending_requests_by_resource(resource)
                workflows.append(workflow)

        # TODO for all types of resources

    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response(
        "scs_resources/manage_resources.html",
        {'workflows': workflows,
         'datas': datas,
         'applications': applications,
        'tkt64': request.COOKIES.get('vph-tkt')},
        RequestContext(request)
    )


def resource_share_widget(request, id='1'):
    """
        given a data endpoint display all related information
    """

    resource = Resource.objects.get(id=id)

    # link data to the relative security configuration STATICALLY!
    # configuration_name = 'TestMatteo'
    # configuration_file = cloudfacade.get_securityproxy_configuration_content(request.user.username, request.COOKIES.get('vph-tkt'), configuration_name)

    # retrieve roles from the configuration
    # properties = extract_configurations(configuration_file)

    resource.permissions_map = get_permissions_map(resource)

    return render_to_response(
        'scs_resources/share_widget.html',
        {'tkt64': request.COOKIES.get('vph-tkt'),
         'resource': resource,
         'requests': [],
         },
        RequestContext(request)
    )


def grant_role(request):
    """
        grant role to user or group
    """

    # if has_permission(request.user, "Manage sharing"):
    name = request.GET.get('name')
    role = Role.objects.get(name=request.GET.get('role'))
    resource = Resource.objects.get(global_id=request.GET.get('global_id'))

    try:
        principal = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        principal = Group.objects.get(name=name)

    # TODO ADD GLOBAL ROLE ACCORDING TO RESOURCE NAME!!!
    # global_role, created = Role.objects.get_or_create(name="%s_%s" % (resource.globa_id, role.name))
    # add_role(principal, global_role)
    add_local_role(resource, principal, role)

    # change request state if exists
    try:
        resource_request = ResourceRequest.objects.get(requestor=principal, resource=resource)
        if is_request_pending(resource_request):
            do_transition(resource_request, request_accept_transition, request.user)
    except ObjectDoesNotExist, e:
        pass
    except Exception, e:
        pass

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

    try:
        principal = User.objects.get(username=name)
    except ObjectDoesNotExist, e:
        principal = Group.objects.get(name=name)

    # TODO REMOVE GLOBAL ROLE ACCORDING TO RESOURCE NAME!!!
    # global_role, created = Role.objects.get_or_create(name="%s_%s" % (resource.globa_id, role.name))
    # remove_role(principal, global_role)
    remove_local_role(resource, principal, role)

    response_body = json.dumps({"status": "OK", "message": "Role revoked correctly", "alertclass": "alert-success"})
    response = HttpResponse(content=response_body, content_type='application/json')
    return response


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
    if cloudfacade.create_securitypolicy(request.user.username, request.COOKIES.get('vph-tkt'), role_name, policy_file):
        response_body = json.dumps({"status": "OK", "message": "Role created correctly", "alertclass": "alert-success", "rolename": role_name})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response
    else:
        response_body = json.dumps({"status": "KO", "message": "Interaction with security agent failed", "alertclass": "alert-error"})
        response = HttpResponse(content=response_body, content_type='application/json')
        return response


def workflowsView(request):

    workflows = []

    try:
        dbWorkflows = Workflow.objects.all()
        for workflow in dbWorkflows:
            workflows.append(workflow)

    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs_resources/workflows.html", {'workflows': workflows}, RequestContext(request))


@login_required
def edit_workflow(request, id=False):
    try:
        if id:
            dbWorkflow = Workflow.objects.get(id=id)
            if request.user != dbWorkflow.owner:
                raise

            metadata = get_resource_metadata(dbWorkflow.global_id)
            metadata['title'] = metadata['name']
            form = WorkflowForm(metadata, instance=dbWorkflow)

        if request.method == "POST":
            form = WorkflowForm(request.POST, request.FILES, instance=dbWorkflow)

            if form.is_valid():
                workflow = form.save(commit=False, owner=dbWorkflow.owner)
                workflow.save()
                request.session['statusmessage'] = 'Changes were successful'
                return redirect('/workflows')

        return render_to_response("scs_resources/workflows.html",
                                  {'form': form},
                                  RequestContext(request))
    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_resources/workflows.html",
                                  {'form': form},
                                  RequestContext(request))

    except Exception, e:
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
                return render_to_response("scs_resources/workflows.html", {'form': form}, RequestContext(request))
        raise

    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_resources/workflows.html", {'form': form}, RequestContext(request))

    except Exception, e:
        return render_to_response("scs_resources/workflows.html", {'form': form}, RequestContext(request))
