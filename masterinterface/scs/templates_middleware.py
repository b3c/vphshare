#from models import message as mess
from django.utils.importlib import import_module
from masterinterface.scs.models import Notification
from raven.contrib.django.raven_compat.models import client

def statusMessage(request):
    """

    :type request: django.core.handlers.wsgi.WSGIRequest
    :return:
    """
    try:
        if request.path == u'/done/':
            return {}
        if request.session.get('statusmessage', False):
            message = request.session['statusmessage']
            del request.session['statusmessage']
            return {
                'statusmessage': message,
                }

        if request.session.get('welcome', False):
            message = request.session['welcome']
            del request.session['welcome']
            return {
                'welcome': message,
                }
        if request.session.get('errormessage', False):
            message = request.session['errormessage']
            del request.session['errormessage']
            return {
                'errormessage': message,
                }
    except Exception, e:
        client.captureException()
        pass
    return {}


def get_notifications(request):
    try:
        notifications = []
        if request.user.is_authenticated() and request.user.username is not 'mi_testuser':
            for n in Notification.objects.filter(recipient=request.user, hidden=False).order_by('-pk'):
                notifications.append({'pk': n.pk, 'subject': n.subject, 'content': n.message})

            return {'notifications': notifications}
    except Exception, e:
        client.captureException()
        pass
    return {'notifications': []}


def baseurl(request):
    """
    Return a BASE_URL template context for the current request.
    """
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'

    return {'BASE_URL': scheme + request.get_host(),}


def okcookies(request):
    """
    Return a BASE_URL template context for the current request.
    """
    if request.session.get('okcookies', False) or request.GET.get('cookie-agree', False):
        request.session['okcookies'] = True
        return {'OK_COOKIES': True}
    else:
        return {'OK_COOKIES': False}




