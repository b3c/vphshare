# Create your views here.
import logging
import json
import os
import string

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from raven.contrib.django.raven_compat.models import client

from masterinterface import settings
import easywebdav


log = logging.getLogger('cyfronet')


def index(request):
    """ Index page to reach all available services
    """
    return render_to_response("cyfronet/index.html",
            {},
        RequestContext(request)
    )

@login_required
def lobcder(request, path = '/'):
    return render_to_response("cyfronet/slet.html", {
                    'lobcderWebDavUrl': settings.LOBCDER_WEBDAV_URL,
                    'lobcderWebDavHref': settings.LOBCDER_WEBDAV_HREF,
                    'lobcderRestUrl': settings.LOBCDER_REST_URL,
                    'lobcderFolderDownloadBaseUrl': settings.LOBCDER_REST_URL + settings.LOBCDER_FOLDER_DOWNLOAD_PATH,
                    'vphTicket': request.ticket,
                    #give the group name to show only the resource sharred with the institution
                    'institutionPortal':  filter(lambda x: x in string.printable and x.isalnum(), request.session['institutionportal'].institution.name) if request.session.get('institutionportal',None) else ''
            }, RequestContext(request))

@csrf_exempt
def retriveVtk(request):

    if request.user.is_authenticated():
        path = request.POST.get('path','')
        if not path:
            path = '/'
        try:
            webdav = easywebdav.connect(settings.LOBCDER_HOST, username='user',
                                        password=request.ticket, protocol='https'
                                        )
            fileName = path.split('/')[-1]
            fileToDownload = os.path.join(settings.LOBCDER_DOWNLOAD_DIR, fileName)
            downloadChunks = webdav.downloadChunks(settings.LOBCDER_ROOT + path)
            #remove file if exists
            if os.path.exists(fileToDownload) and os.stat(fileToDownload)[6] != int(downloadChunks.raw.headers['content-length']):
                os.remove(fileToDownload)

            if not os.path.exists(fileToDownload):
                webdav.download(settings.LOBCDER_ROOT+ path, fileToDownload)

            content = json.dumps({'path': fileName}, sort_keys=False)

            response = HttpResponse(content=content,
                                    content_type='application/json')
            return response

        except Exception, e:
            client.captureException()
            response = HttpResponse(status=500)
            response._is_string = True

            return response

    #User is not authenticade
    response = HttpResponse(status=403)
    response._is_string = True

    return response

@login_required
def tools(request):
    return render_to_response('cyfronet/clew.html', {
                        'cloudFacadeUrl': settings.CLOUDFACACE_URL,
                        'vphTicket': request.ticket,
                        'institutionPortal':  request.session['institutionportal'].institution.name if request.session.get('institutionportal',None) else ''
                }, RequestContext(request))

