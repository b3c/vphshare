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
from masterinterface.scs import __version__ as version
from masterinterface.scs_groups.models import Institution
from permissions.models import Role
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from masterinterface import wsdl2mi
from utils import is_staff
from masterinterface import settings
from masterinterface.atos.metadata_connector_json import search_resource
from masterinterface.scs_resources.models import get_pending_requests_by_user
from masterinterface.scs_groups.views import is_pending_institution, is_pending_action
from masterinterface.cyfronet.lobcder import getShortTicket

def home(request):
    """Home view """

    data = {'version': version}
    if request.user.is_authenticated():
        data['last_login'] = request.session.get('social_auth_last_login_backend')

        # check if the user has pending requests to process
        pending_requests = get_pending_requests_by_user(request.user)
        if pending_requests:
            data['statusmessage'] = 'Dear %s, you have %s pending request(s) waiting for your action: %s' % (request.user.first_name, len(pending_requests), ''.join(['</br><a href="/resources/%s">%s %s requested %s</a>'%(r.resource.global_id, r.requestor.first_name, r.requestor.last_name, r.resource.metadata['name']) for r in pending_requests]))

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
    if request.user.is_authenticated():
        return redirect(request.GET.get('next','/'))
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
def profile(request, user=None):
    """Login complete view, displays user data"""

    tkt64 = request.ticket
    filestore_tkt = getShortTicket(tkt64)

    if user is None:
        user = request.user
    else:
        user = User.objects.get(username=user)

    data = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend'),
        'tkt64': tkt64,
        'filestore_tkt': filestore_tkt,
        'user': user,
        'users':  [u.username for u in User.objects.all()]
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


@csrf_exempt
def search_service(request):

    if request.method == 'POST':
        #min = int(request.POST['min'])
        #max = int(request.POST['max'])
        page = int(request.POST['page'])
        countType = request.session['countType']
        search_text = request.session['search_text']
        expression = request.session['expression']
        pages = request.session['pages']
        results = request.session['results']
        if page > request.session['page']:
            results = search_resource(search_text, expression, numResults=20,  page=page)
            for ctype, counter in countType.items():
                request.session['countType'][ctype] += counter
            countType = request.session['countType']
            request.session['results'] += results
            request.session['page'] = page


        filterby = request.POST.get('filterby', None)
        if filterby != '[]':
            filterby = json.loads(filterby)
            numResults = 0
            tmpresults = list(results)
            results = []
            for filter in filterby:
                numResults += request.session['types'].get(filter,0)
            for result in tmpresults:
                if result['type'] not in ['Dataset', 'Workflow', 'AtomicService', 'File', 'SemanticWebService', 'User', 'Institution'] and 'Other' in filterby:
                    results.append(result)
                if result['type'] in filterby:
                    results.append(result)

        resultsRender = render_to_string("scs/search_results.html", {"results": results})

        return HttpResponse(status=200,
                            content=json.dumps({'data': resultsRender, 'numResults': len(request.session['results']), 'countType': countType}, sort_keys=False),
                            content_type='application/json')

    response = HttpResponse(status=403)
    response._is_string = True
    return response


def search(request):


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

    return render_to_response("scs/search.html",
                              {'search': search, "results":None, "numResults": 0, 'countType': {}, 'filterToshow':'false',
                              'types': ['Dataset', 'Workflow', 'AtomicService', 'File', 'SemanticWebService']},
                              RequestContext(request))


@is_staff()
def users_access_admin(request):


    Roles = Role.objects.all()
    return render_to_response("scs/usersadmin.html",
                              {'Roles': Roles.values()},
                              RequestContext(request))


def page400(request):

    return render_to_response("scs/400.html", {}, RequestContext(request))


def page403(request):

    return render_to_response("scs/403.html", {}, RequestContext(request))


def page404(request):

    return render_to_response("scs/404.html", {}, RequestContext(request))


def page500(request):
    from masterinterface.scs.forms import ContactUs
    contactForm= ContactUs(request)
    return render_to_response("scs/500.html", {'contactForm':contactForm}, RequestContext(request))

@login_required
def support(request):
    from masterinterface.scs.forms import ContactUs
    reported= False
    if request.method=="POST":
        contactForm= ContactUs(request, request.POST)
        if contactForm.is_valid():
            from django.template import loader
            from django.core.mail import EmailMultiAlternatives
            text_content = loader.render_to_string('scs/%s.txt' % 'support_mail', dictionary={'contactForm':contactForm , 'reported': reported})
            html_content = loader.render_to_string('scs/%s.html' % 'support_mail', dictionary={'contactForm':contactForm , 'reported': reported})
            mail_from='webmaster@vph-share.eu'
            mail_to='%s %s <%s>' % ('vph-share', 'support', 'support@vph-share.eu')
            msg = EmailMultiAlternatives('Support request  [VPH-Bug-Report]', text_content, mail_from, [mail_to])
            msg.attach_alternative(html_content, "text/html")
            msg.content_subtype = "html"
            msg.send()
            reported= True
    else:
        contactForm= ContactUs(request)

    return render_to_response("scs/support.html", {'contactForm':contactForm , 'reported': reported}, RequestContext(request))
## Manage-data modals services ##


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
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        response = HttpResponse(status=403)
        response._is_string = True
        return response


def api_help(request):
    return render_to_response(
        'scs/api.html',
        RequestContext(request)
    )

def beta_programme(request):
    return render_to_response("scs/beta_programme.html",
            {},
        RequestContext(request))

def upload_structured_data(request):
    return render_to_response("scs/upload_structured_data.html",
            {},
        RequestContext(request))
