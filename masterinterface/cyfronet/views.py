# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from masterinterface import settings
from forms import LobcderUpload
from forms import LobcderDelete
from forms import LobcderCreateDirectory
import easywebdav
from lobcder import lobcderEntries
import mimetypes
from StringIO import StringIO
import logging

log = logging.getLogger('cyfronet')

def index(request):
    """ Index page to reach all available services
    """
    return render_to_response("cyfronet/index.html",
            {},
        RequestContext(request)
    )

@login_required
def cloudmanager(request):
    """ Atmosphere Cloud Management Portlet embedding (*only for authenticated users*)
    """
    return render_to_response("cyfronet/cloudmanager.html",
            {'source': settings.CLOUD_PORTLET_LOGIN_URL_TEMPLATE.format(request.user.username, request.COOKIES.get('vph-tkt','No ticket'), 'cloud')},
        RequestContext(request))

@login_required
def datamanager(request):
    """ LOBDCER Storage Service Portlet embedding (*only for authenticated users*)
    """
    return render_to_response("cyfronet/datamanager.html",
            {'source': settings.CLOUD_PORTLET_LOGIN_URL_TEMPLATE.format(request.user.username, request.COOKIES.get('vph-tkt','No ticket'), 'data')},
        RequestContext(request))

@login_required
def policymanager(request):
    """ Security Policy Management Portlet embedding (*only for authenticated users*)
    """
    return render_to_response("cyfronet/policymanager.html",
            {'source': settings.CLOUD_PORTLET_LOGIN_URL_TEMPLATE.format(request.user.username, request.COOKIES.get('vph-tkt','No ticket'), 'policy')},
        RequestContext(request))

@login_required
def lobcder(request, path = '/'):
    """
        LOBCDER Management Portlet
    """
    if not path:
        path = '/'
    webdav = easywebdav.connect(settings.LOBCDER_HOST, settings.LOBCDER_PORT, username = 'user', password = request.COOKIES.get('vph-tkt','No ticket'))
    if request.method == 'POST':
        log.info('Uploading LOBCDER file ' + request.FILES['file'].name + ' to path ' + path)
        form = LobcderUpload(request.POST, request.FILES)
        if form.is_valid():
            webdav.uploadChunks(request.FILES['file'], settings.LOBCDER_ROOT + path + request.FILES['file'].name)
    else:
        form = LobcderUpload()
    if not path.endswith('/'):
        #downloading a file
        fileName = path.split('/')[-1]
        response = HttpResponse(webdav.downloadChunks(settings.LOBCDER_ROOT + path), content_type = mimetypes.guess_type(fileName)[0])
        response['Content-Disposition'] = 'attachment; filename=' + fileName
        return response
    else:
        #listing a directory
        entries = lobcderEntries(webdav.ls(settings.LOBCDER_ROOT + path), settings.LOBCDER_ROOT, path, request.COOKIES.get('vph-tkt','No ticket'))
        return render_to_response("cyfronet/lobcder.html", {'path': path, 'entries': entries, 'form': form, 'deleteForm': LobcderDelete(), 'createDirectoryForm': LobcderCreateDirectory()}, RequestContext(request))

@login_required
def lobcderDelete(request, path = '/'):
    log.info('Deleting LOBCDER resource with path ' + path)
    webdav = easywebdav.connect(settings.LOBCDER_HOST, settings.LOBCDER_PORT, username = 'user', password = request.COOKIES.get('vph-tkt','No ticket'))
    if path.endswith('/'):
        webdav.rmdir(settings.LOBCDER_ROOT + path)
    else:
        webdav.delete(settings.LOBCDER_ROOT + path)
    return redirect('/cyfronet/lobcder' + path.rstrip('/')[0:path.rstrip('/').rfind('/')])

@login_required
def lobcderCreateDirectory(request, path = '/'):
    log.info('Creating LOBCDER directory in path ' + path)
    form = LobcderCreateDirectory(request.POST)
    if form.is_valid():
        webdav = easywebdav.connect(settings.LOBCDER_HOST, settings.LOBCDER_PORT, username = 'user', password = request.COOKIES.get('vph-tkt','No ticket'))
        webdav.mkdir(settings.LOBCDER_ROOT + path + form.cleaned_data['name'])
    return redirect('/cyfronet/lobcder' + path)