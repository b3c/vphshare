#from models import message as mess
from django.utils.importlib import import_module
from masterinterface.scs.models import Notification

def statusMessage(request):
    """

    :type request: django.core.handlers.wsgi.WSGIRequest
    :return:
    """
    try:
        if request.session.get('statusmessage', False):
            message = request.session['statusmessage']
            del request.session['statusmessage']
            return {
                'statusmessage': message,
                }

        if request.session.get('errormessage', False):
            message = request.session['errormessage']
            del request.session['errormessage']
            return {
                'errormessage': message,
                }
    except Exception, e:
        pass
    return {}


def get_notifications(request):
    try:
        notifications = []
        for n in Notification.objects.filter(recipient=request.user, hidden=False).order_by('-pk'):
            notifications.append({'pk': n.pk, 'subject': n.subject, 'content': n.message})

        return {'notifications': notifications}
    except Exception, e:
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

