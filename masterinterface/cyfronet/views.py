# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

from masterinterface import settings

from forms import LobcderUpload

import easywebdav


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

    fileName = None
    webdav = easywebdav.connect(settings.LOBCDER_HOST, settings.LOBCDER_PORT, username = 'user', password = request.COOKIES.get('vph-tkt','No ticket'))
    
    if request.method == 'POST':
        form = LobcderUpload(request.POST, request.FILES)
        if form.is_valid():
            webdav.uploadChunks(request.FILES['file'], settings.LOBCDER_ROOT + path + request.FILES['file'].name)
    else:
        form = LobcderUpload()

    entries = webdav.ls(settings.LOBCDER_ROOT + path)    
    
    return render_to_response("cyfronet/lobcder.html",
            {'path': path, 'entries': entries, 'form': form, 'fileName': fileName},
        RequestContext(request))
