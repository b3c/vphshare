from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
from forms import PolicyForm, AdvancePolicyForm
from models import SecurityPolicy
from politicizer import create_policy_file, extract_permission_map
from configurationizer import create_configuration_file, extract_configurations
from masterinterface.scs.utils import get_file_data
from masterinterface.cyfronet import cloudfacade
from masterinterface.scs.utils import is_staff
from django.contrib.auth.decorators import login_required
from masterinterface.scs_security.widgets import AdditionalUserAttribute, AdditionalPostField
from masterinterface.scs_security.models import SecurityPolicy, SecurityConfiguration
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

@login_required()
def index(request):
    """
        security home page
    """
    policies = []
    cyfronet_users = cloudfacade.get_users(request.ticket)
    for policy in cloudfacade.get_securitypolicies(request.ticket):
        security_policy, created = SecurityPolicy.objects.get_or_create(ticket=request.ticket, remote_id=policy['id'])
        owners = security_policy.owner.values_list('username', flat=True)
        for user_id in policy['owners']:
            username=cyfronet_users[user_id-1]['login']
            try:
                user = User.objects.get(username=username)
                if user.username not in owners:
                    security_policy.owner.add(user)
                owners.append(username)
            except Exception, e:
                continue
        security_policy.name = policy['name']
        if security_policy.parse_xacml() is False:
            security_policy.advance_use = True
        else:
            security_policy.advance_use = False
        security_policy.save()
        policy['owners'] = owners
        policies.append(policy)

    configurations = []

    for configuration in cloudfacade.get_securityproxy_configurations(request.ticket):
        owners = []
        for user_id in configuration['owners']:
            owners.append(cyfronet_users[user_id-1]['login'])
        configuration['owners'] = owners
        configurations.append(configuration)
    return render_to_response(
        'scs_security/index.html',
        {'policies': policies,
         'configurations': configurations},
        RequestContext(request)
    )

@csrf_exempt
def new_attribute(request):
    if request.POST.get('key', None):
        new_attribute = AdditionalUserAttribute()
        return HttpResponse(content=new_attribute.render(request.POST.get('key', None),None))
    return HttpResponse(status=403)

@csrf_exempt
def new_post_field(request):
    if request.POST.get('key', None):
        new_post_field = AdditionalPostField()
        return HttpResponse(content=new_post_field.render(request.POST.get('key', None),None))
    return HttpResponse(status=403)

@login_required
def new_policy(request, remote_id=None):
    """
        Create a new policy and uses the PolicyForm object to render the form and genereate the xacml file to upload to the cloud server.
    """

    if remote_id is not None:
        if 'edit' in request.path:
            edit = True
            view = False
        else:
            edit = False
            view = True
        policy = SecurityPolicy.objects.get(ticket=request.ticket, remote_id=remote_id)
        policy.owners = policy.owner.all()
        if edit and request.user not in policy.owner.all():
            # the user have no permission to edit the policy
            raise PermissionDenied
        data = policy.parse_xacml()
        if policy.advance_use == True and data == False:
            expert = 'true'
        else:
            expert = 'false'
        form = PolicyForm(data=data)
        advancedform = AdvancePolicyForm(data={'name':policy.name})
    else:
        view = False
        edit = False
        policy = None
        data = {}
        expert = 'false'
        form = PolicyForm()
        advancedform = AdvancePolicyForm()

    if request.method == 'POST':
        try:
            if request.POST.get('advance_user', None) is None:
                form = PolicyForm(data=request.POST)
                if form.is_valid() and form.cleaned_data.get('advance_user') == False:
                    if request.POST.get('role', None):
                        data['role'] = form.cleaned_data['role']
                    if request.POST.get('name', None):
                        data['name'] = request.POST['name']
                    if request.POST.has_key('user_attribute_name[0]') and request.POST.has_key('user_attribute_condition[0]') and request.POST.has_key('user_attribute_value[0]'):
                        data['user_attributes'] = []
                        names      = request.POST.getlist("user_attribute_name[0]")
                        conditions = request.POST.getlist("user_attribute_condition[0]")
                        values     = request.POST.getlist("user_attribute_value[0]")
                        for name, condition, value in zip(names, conditions, values):
                            if len(name) > 0:
                                data['user_attributes'] += [(name, condition%value)]
                    if request.POST.has_key('post_field_name[0]') and request.POST.has_key('post_field_condition[0]') and request.POST.has_key('post_field_value[0]'):
                        data['post_options'] = []
                        names      = request.POST.getlist("post_field_name[0]")
                        conditions = request.POST.getlist("post_field_condition[0]")
                        values     = request.POST.getlist("post_field_value[0]")
                        for name, condition, value in zip(names, conditions, values):
                            if len(name) > 0:
                                data['post_options'] += [(name, condition%value)]
                    if request.POST.get('url_contain', None):
                        data['url_contain'] = request.POST['url_contain']
                    if request.POST.get('time_start_0', None) and request.POST.get('time_end_0', None):
                        data['time_range'] = (request.POST['time_start_0'],request.POST['time_end_0'])
                    if request.POST.get('expiry_0', None):
                        data['date_expiration'] = request.POST['expiry_0']

                    xacml_result = render_to_response("scs_security/xacml_template.xml", data)
                    if policy is None:
                        policy = SecurityPolicy(name=form.cleaned_data['name'], advance_use = False)
                        policy.save(configuration=xacml_result.content, ticket=request.ticket)
                        policy.owner.add(request.user)
                        request.session['statusmessage'] = "Security Policy file correctly created"
                    else:
                        policy.advance_use = False
                        policy.save(configuration=xacml_result.content, ticket=request.ticket)
                        request.session['statusmessage'] = "Security Policy file correctly updated"
            else:
                advancedform = AdvancePolicyForm(data=request.POST, files=request.FILES)
                expert = 'true'
                if advancedform.is_valid():
                    xacml_result = advancedform.cleaned_data['advanced_xacml_upload']
                    if policy is None:
                        policy = SecurityPolicy(name=advancedform.cleaned_data['name'], advance_use = True)
                        policy.save(configuration=xacml_result,ticket=request.ticket)
                        policy.owner.add(request.user)
                        request.session['statusmessage'] = "Security Policy file correctly created"
                    else:
                        policy.advance_use = True
                        policy.save(configuration=xacml_result,ticket=request.ticket)
                        request.session['statusmessage'] = "Security Policy file correctly updated"
        except Exception, e:
            request.session['errormessage'] = "Some errors occurred, remember: the policy name have to be unique in the list of the policies."
        else:
            #return to the policy list after the edit or creation.
            return redirect('policy')

    return render_to_response(
        'scs_security/new_policy.html',
        {'form':form, 'advancedform': advancedform, 'expert': expert, 'policy':policy, 'edit':edit, 'view':view},
        RequestContext(request)
    )

@login_required()
def delete_policy(request, remote_id=None):
    """
        delete the policy file
    """

    data = {}

    if request.method == 'GET' and remote_id is not None:
        policy = SecurityPolicy.objects.get(ticket=request.ticket, remote_id=remote_id)
        if request.user not in policy.owner.all():
            request.session['errormessage'] = "you need to be owner of the policy"
            raise PermissionDenied
        policy.delete(ticket=request.ticket)
        return redirect('policy')
    raise PermissionDenied

@login_required()
def configuration(request, remote_id=None):
    """
        get/set the security proxy configuration
    """

    data = {}
    if remote_id is not None:
        if 'edit' in request.path:
            edit = True
            view = False
        else:
            edit = False
            view = True
    else:
        edit=False
        view=False
    if request.method == 'GET':

        configuration_id = remote_id
        if configuration_id:
            configuration_obj = cloudfacade.get_securityproxy_configurations_by_id(request.ticket, configuration_id)
            owners = []
            for user_id in configuration_obj['owners']:
                owners.append(cloudfacade.get_user(request.ticket, user_id)['login'])
            configuration_obj['owners'] = owners
            data['configuration_obj'] = configuration_obj
            data['configuration_file'] = configuration_obj['payload'].decode('unicode_escape')
            try:
                data['properties'] = extract_configurations(data['configuration_file'])
            except Exception, e:
                data['properties'] = {}
                data['errormessage'] = "The configuration file loaded seems not to be valid, please upload a new one"

    else:

        # update/set with permissions map
        if 'sumbitwithprops' in request.POST:
            props = {
                'outgoing_port': request.POST.get('outgoing_port', ''),
                'granted_roles': request.POST.get('granted_roles', ''),
                'listening_port': request.POST.get('listening_port', ''),
                'outgoing_address': request.POST.get('outgoing_address', ''),

            }
            configuration_file = create_configuration_file(props)

        # update/set by file content
        elif 'sumbitwithcontent' in request.POST:
            configuration_file = request.POST.get('filecontent')

        # update/set by file upload
        elif 'sumbitwithfile' in request.POST:
            configuration_file = get_file_data(request.FILES.get('fileupload'))

        # check if the file is correct or not
        configuration_file_ok = False
        try:
            extract_configurations(configuration_file)
            configuration_file_ok = True
        except Exception, e:
            configuration_file_ok = False

        if configuration_file_ok:
            if "newconfiguration" in request.POST:
                if cloudfacade.create_securityproxy_configuration(request.ticket, request.POST['name'], configuration_file):
                    data['statusmessage'] = "Security configuration file correctly created."
                    return  redirect('security_configuration')
                else:
                    data['errormessage'] = "Error while creating security configuration"
            else:
                configuration_id = request.POST['id']
                configuration_obj = cloudfacade.get_securityproxy_configurations_by_id(request.ticket, configuration_id)
                if cloudfacade.update_securityproxy_configuration(request.ticket, configuration_obj['id'], configuration_obj['name'], configuration_file):
                    data['statusmessage'] = "Security Proxy configuration correctly updated."
                    return  redirect('security_configuration')
                else:
                    data['errormessage'] = "Error while updating security configuration"
        else:
            data['errormessage'] = "The configuration file uploaded seems not to be valid"

    data['configurations'] = cloudfacade.get_securityproxy_configurations(request.ticket)
    data['edit'] = edit
    data['view'] = view
    return render_to_response(
        'scs_security/configuration.html',
        data,
        RequestContext(request)
    )


@is_staff()
def delete_configuration(request, remote_id=None):
    """
        delete the security proxy configuration file
    """

    data = {}

    if request.method == 'GET' and remote_id is not None:
        configuration_id = remote_id

        if cloudfacade.delete_securityproxy_configuration(request.ticket, configuration_id):
            data['statusmessage'] = "Security Proxy configuration correctly deleted"

        else:
            data['errormessage'] = "Error while deleting Security Proxy configuration"
    else:
        raise PermissionDenied

    return redirect('security_configuration')


