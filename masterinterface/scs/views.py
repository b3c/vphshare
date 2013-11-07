import string
import json

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.messages.api import get_messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import ordereddict
from scs import __version__ as version
from permissions.models import Role
from django.http import HttpResponse
from django.template.loader import render_to_string

from masterinterface import wsdl2mi
from utils import is_staff
from masterinterface import settings
from masterinterface.atos.metadata_connector import *
from masterinterface.scs_resources.utils import get_pending_requests_by_user
from masterinterface.scs_groups.views import is_pending_institution, is_pending_action

def home(request):
    """Home view """

    data = {'version': version}
    if request.user.is_authenticated():
        data['last_login'] = request.session.get('social_auth_last_login_backend')

        # check if the user has pending requests to process
        pending_requests = get_pending_requests_by_user(request.user)
        if pending_requests:
            data['statusmessage'] = 'Dear %s, you have %s pending request(s) waiting for your action.' % (request.user.first_name, len(pending_requests))

        if is_pending_institution(request, None):
            data['errormessage'] = 'Dear %s, you have pending Intitution(s) waiting for your action <a href="/groups">go here</a>.' % request.user.first_name

        if is_pending_action(request, None):
            data['errormessage'] = 'Dear %s, you have pending user(s) waiting for your action <a href="/groups">go here</a>.' % request.user.first_name


    if not request.user.is_authenticated() and request.GET.get('loggedout') is not None:
        data['statusmessage'] = 'Logout done.'

    return render_to_response(
        'scs/index.html',
        data,
        RequestContext(request)
    )


def login(request):
    """Login view"""

    return render_to_response(
        'scs/login.html',
        {'version': version, 'next': request.GET.get('next','/')},
        RequestContext(request)
    )


def registration(request):
    """Login view"""
    if request.user.is_authenticated():
        return redirect('/profile/')
    return render_to_response(
        'scs/registration.html',
        {'version': version},
        RequestContext(request)
    )

def reset_password(request):
    """Login view"""
    if request.user.is_authenticated():
        return redirect('/')
    return render_to_response(
        'scs/reset_password.html',
        {'version': version, 'token':request.GET.get('token', '')},
        RequestContext(request)
    )

@login_required
def profile(request):
    """Login complete view, displays user data"""

    tkt64 = request.COOKIES.get('vph-tkt','No ticket')

    data = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend'),
        'tkt64': tkt64
    }



    return render_to_response(
        'scs/profile.html',
        data,
        RequestContext(request)
    )


@login_required
def login_error(request):
    """Very simpole login error view"""
    messages = get_messages(request)
    return render_to_response(
        'scs/error.html',
        {'version': version,
         'messages': messages},
        RequestContext(request)
    )


@login_required
def test(request):
    """ just a test page """
    return render_to_response("scs/test.html", {'ajax':request.is_ajax}, RequestContext(request))


@login_required
def services(request):
    """ a page with all available applications """
    serviceList = []

    message={}
    if 'delete' in request.GET:
        serviceToDelete=request.GET['delete']
        success = wsdl2mi.DeleteService(serviceToDelete)
        if success[0]:

            message['statusmessage']=success[1]

        else:

            message['errormessage']=success[1]

    if 'wsdlURL' in request.POST:
        wsdlURL=request.POST['wsdlURL']
        try:
            val = URLValidator(verify_exists=False)
            val(wsdlURL)
            success = wsdl2mi.startInstallService(wsdlURL)
            if success[0]:

                message['statusmessage']=success[1]

            else:

                message['errormessage']=success[1]

        except ValidationError, e:
            message['errormessage']="This wsdl URL is not valid"

    for app in settings.INSTALLED_APPS:
        # TODO do a better check
        if app.count('masterinterface') and not app.count('scs') and not app.count('cyfronet'):
            service = app.split('.')[1]
            serviceList.append( service )

    message['services']=serviceList

    return render_to_response("scs/services.html",
            message,
        RequestContext(request))


def contacts(request):

    if request.method == 'GET':
        return render_to_response("scs/contacts.html",
            {},
        RequestContext(request))
    else:
        return render_to_response("scs/contacts.html",
                {'statusmessage':'Thanks, your message has been sent!'},
            RequestContext(request))


def help(request):
    return render_to_response("scs/help.html",
            {},
        RequestContext(request))


def data(request):
    return render_to_response("scs/data.html",
        {},
                              RequestContext(request))


def search_data(request):
    return render_to_response("scs/search_data.html",
        {},
                              RequestContext(request))


def upload_data(request):
    return render_to_response("scs/upload_data.html",
        {},
                              RequestContext(request))


def manage_data(request):
    from masterinterface.scs_resources.models import Workflow

    workflows = []

    try:
        dbWorkflows = Workflow.objects.all()
        for workflow in dbWorkflows:
            workflow.permissions_map = get_permissions_map(workflow.global_id)
            workflows.append(workflow)

    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs/manage_data.html",
                              {'workflows': workflows,
                               'tkt64': request.COOKIES.get('vph-tkt')},
                              RequestContext(request))

@csrf_exempt
def search_service(request):

    if request.method == 'POST':
        min = int(request.POST['min'])
        max = int(request.POST['max'])
        filterby = request.POST.get('filterby', None)
        if filterby == '[]':
            numResults = len(request.session['results'])
            results = request.session['results'][min:max]
        else:
            filterby = json.loads(filterby)
            results = []
            numResults = 0
            for filter in filterby:
                numResults += request.session['types'].get(filter,0)
            for result in request.session['results']:
                if result['type'] not in ['Dataset', 'Workflow', 'Atomic Service', 'File', 'SWS', 'Application', 'User', 'Institution'] and 'Other' in filterby:
                    results.append(result)
                if result['type'] in filterby:
                    results.append(result)

        resultsRender = render_to_string("scs/search_results.html", {"results": results})

        return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender, 'numResults': str(numResults)}, sort_keys=False),
                            content_type='application/json')

    response = HttpResponse(status=403)
    response._is_string = True
    return response


def search(request):

    if request.GET.get('search_text', None):
        search_text = request.GET.get('search_text', '')
        types = request.GET.get('types', [])
        if type(types) in (str, unicode):
            types = types.split(',')[:-1]
        filterby = request.GET.get('filterby', [])
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
        expression = {
            'type': types,
            'category': categories,
            'author': authors,
            'licence': licences,
            'tags': tags
        }
        results, countType = search_resource(search_text, expression)

        from django.db.models import Q
        if types == [] and (filterby == [] or 'User' in filterby):
            from django.contrib.auth.models import User
            users = User.objects.filter(
                Q(username__icontains=search_text) | Q(email__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text)
            )
            users = [{"description": user.username, "name": "%s %s" % (user.first_name, user.last_name), "email": user.email, "type": 'User'} for user in users]
            results += users
            if 'User' not in countType:
                countType['User'] = len(users)

        if (types == [] or 'Institution' in types) and (filterby == [] or 'Institution' in filterby or 'Institution' in types):
            from scs_groups.models import Institution
            institutions = Institution.objects.filter(
                Q(name__icontains=search_text) | Q(description__icontains=search_text)
            )
            institutions = [{"description": institution.description, "name": institution.name, "id": institution.id, "type":'Institution'} for institution in institutions]
            results += institutions
            if 'Institution' not in countType:
                countType['Institution'] = len(institutions)

        #if types == [] and (filterby == [] or 'Study' in filterby):
        #    from scs_groups.models import Study
        #    studies = Study.objects.filter(
        #        Q(name__icontains=search_text) | Q(description__icontains=search_text)
        #    )
        #    studies = [{"description": studie.description, "name": studie.name, "id": studie.id, 'institution': studie.institution.id,  "type":'Study'} for studie in studies]
        #    results += studies
        #    if 'Study' not in countType:
        #        countType['Study'] = len(studies)

        request.session['results'] = results
        request.session['types'] = countType
        return render_to_response("scs/search.html",
                                  {'search': search, "results": results[0:30], "numresults": len(results), 'countType': countType,
                                  'types': ['Dataset', 'Workflow', 'Atomic Service', 'File', 'SWS', 'Application', 'User', 'Institution', 'Other']},
                                  RequestContext(request))
    types = request.GET.get('types', [])
    if type(types) in (str, unicode):
            types = types.split(',')[:-1]
    search = {
            'type': types,
    }
    return render_to_response("scs/search.html",
                              {'search': search, "results": None, "numresults": 0, 'countType': {},
                               'types': ['Dataset', 'Workflow', 'Atomic Service', 'File', 'SWS', 'Application', 'User', 'Institution', 'Other']},
                              RequestContext(request))

@is_staff()
def users_access_admin(request):


    Roles = Role.objects.all()
    return render_to_response("scs/usersadmin.html",
                              {'Roles': Roles.values()},
                              RequestContext(request))


def browse_data_az(request):
    """
        browse data in alphabetical order
    """
    resources_by_letter = {}
    try:
        all_resources = []
        all_resources.extend(filter_resources_by_type('File'))
        all_resources.extend(filter_resources_by_type('Dataset'))

        resources_by_letter = ordereddict.OrderedDict()

        for letter in string.uppercase:
            resources_by_letter[letter] = []

        resources_by_letter['0-9'] = []

        for r in all_resources:
            key = str(r.get('name', ' ')).upper()[0]
            if key in resources_by_letter:
                resources_by_letter[key].append(r)
            else:
                resources_by_letter['0-9'].append(r)
    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs/browseaz.html", {"resources_by_letter": resources_by_letter, "letters": string.uppercase}, RequestContext(request))

def page400(request):

    return render_to_response("scs/400.html", {}, RequestContext(request))


def page403(request):

    return render_to_response("scs/403.html", {}, RequestContext(request))


def page404(request):

    return render_to_response("scs/404.html", {}, RequestContext(request))


def page500(request):

    return render_to_response("scs/500.html", {}, RequestContext(request))

## Manage-data modals services ##

@csrf_exempt
def delete_tag_service(request):
    """
        remove tag to resource's metadata
    """
    try:
        if request.method == 'POST':

            removed_tag = request.POST.get('tag', "")
            global_id = request.POST.get('global_id', "")

            metadata = get_resource_metadata(global_id)
            new_tag = {'tags': ''}
            for tag in metadata['tags'].split():
                if tag != removed_tag:
                    new_tag['tags'] += "%s " % tag
            new_tag['tags'] = new_tag['tags'].strip()
            update_resource_metadata(global_id, new_tag)

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


@csrf_exempt
def add_tag_service(request):
    """
        add tag to resource's metadata
    """
    try:
        if request.method == 'POST':

            added_tag = request.POST.get('tag', "")
            global_id = request.POST.get('global_id', "")

            metadata = get_resource_metadata(global_id)
            if metadata['tags'] is not None:
                for tag in metadata['tags'].split():
                    if tag == added_tag:
                        raise
                new_tags = {'tags': "%s %s" % (metadata['tags'], added_tag)}
            else:
                new_tags = {'tags': added_tag.strip()}
            update_resource_metadata(global_id, new_tags)

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


@csrf_exempt
def edit_description_service(request):
    """
        add tag to resource's metadata
    """
    try:
        if request.method == 'POST':

            description = request.POST.get('description', "")
            global_id = request.POST.get('global_id', "")
            update_resource_metadata(global_id, {'description': description})

            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


@csrf_exempt
def hide_notification(request):
    """
        add tag to resource's metadata
    """
    try:
        if request.user.is_authenticated() and request.method == 'POST' and request.POST.get('notificationId', None):
            from masterinterface.scs.models import Notification
            notification = Notification.objects.get(pk=request.POST.get('notificationId', None))
            notification.hidden = True
            notification.save()
            response = HttpResponse(status=200)
            response._is_string = True
            return response

        raise

    except Exception, e:
        response = HttpResponse(status=403)
        response._is_string = True
        return response


def api_help(request):
    return render_to_response(
        'scs/api.html',
        RequestContext(request)
    )

def search_workflow(request):
    return render_to_response("scs/search_workflows.html",
        {},
                              RequestContext(request))

def beta_programme(request):
    return render_to_response("scs/beta_programme.html",
            {},
        RequestContext(request))
