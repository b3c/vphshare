# Create your views here.
from xmlrpclib import ServerProxy
from datetime import datetime
import subprocess
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .models import ParaviewInstance

PVW_START_PORT = 5000


def pvw_start_session(request):
    """
        pvw_start_session provide the inizialization of paraviewweb_xmlrpc.py process
    """
    try:
        if request.method == 'GET' and request.user.is_authenticated():
            pvw_instance = None
            try:
                pvw_instance = ParaviewInstance.objects.get(user=request.user, deletion_time__exact=None)
                if request.session[str(pvw_instance.pid)].poll() is None:
                    request.session[str(pvw_instance.pid)].kill()
                    request.session[str(pvw_instance.pid)].wait()
                    pvw_instance.deletion_time = datetime.now()
                    pvw_instance.save()
                    raise Exception
            except Exception,e:
                if pvw_instance is not None:
                    pvw_instance.deletion_time = datetime.now()
                    pvw_instance.save()
                port = settings.PARAVIEWWEB_PORT  + ParaviewInstance.objects.filter(deletion_time__isnull=True).count()
                pvw_proces = subprocess.Popen(
                    [settings.PARAVIEW_PYTHON_BIN,
                     settings.PARAVIEWWEB_SERVER,
                    "-p "+str(port)],
                    #stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                pvw_instance = ParaviewInstance(pid=pvw_proces.pid, port=port, user=request.user)
                pvw_instance.save()
                request.session[str(pvw_proces.pid)] = pvw_proces
                pvw_render_connector = ServerProxy('http://127.0.0.1:%s/api' % pvw_instance.port)
                #Wait that the process run.
                while True:
                    try:
                        result = pvw_render_connector.ready()
                        break
                    except Exception, e:
                        pass
                pass

            return HttpResponse(content='TRUE')
    except Exception,e:
        client.captureException()
        pass

    response = HttpResponse(status=403)
    response._is_string = True

    return response


def pvw_close_session(request):
    """
        pvw_start_session provide the inizialization of paraviewweb_xmlrpc.py process
    """
    pvw_instance = None
    try:
        if request.method == 'GET' and request.user.is_authenticated():
            pvw_instance = ParaviewInstance.objects.get(user=request.user, deletion_time__exact=None)
            request.session[str(pvw_instance.pid)].kill()
            request.session[str(pvw_instance.pid)].wait()
            pvw_instance.deletion_time = datetime.now()
            pvw_instance.save()
            return HttpResponse(content='TRUE')
    except Exception,e:
        if pvw_instance:
            pvw_instance.deletion_time = datetime.now()
            pvw_instance.save()

        pass

    response = HttpResponse(status=403)
    response._is_string = True

    return response

@csrf_exempt
def pvw_method_call(request):

    try:
        if request.method == 'POST' and request.user.is_authenticated():

            data = json.loads(request.POST['data'])
            pvw_instance = ParaviewInstance.objects.get(user=request.user, deletion_time__exact=None)
#            if request.session[str(pvw_instance.pid)].poll() is None:
            pvw_render_connector = ServerProxy('http://127.0.0.1:%s/api' % pvw_instance.port)
	    result = pvw_render_connector.pvw_call_method(data['method'], json.dumps(data['args']))
#            else:
#                raise Exception
            #sistemare se stinga o dizionario!!
            if result is None:
                response = HttpResponse(content="")
            else:
                response = HttpResponse(content=result)

            return response
    except Exception,e:
        pass

    response = HttpResponse(status=403)
    response._is_string = True

    return response
