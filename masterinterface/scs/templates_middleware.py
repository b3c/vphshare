#from models import message as mess
from django.utils.importlib import import_module

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


#def getMessages(request):
#    try:
#        messages = []
#        for m in mess.objects.all():
#            callback_r = True
#            if m.expire_callback != '':
#                i = m.expire_callback.rfind('.')
#                module, attr = m.expire_callback[:i], m.expire_callback[i+1:]
#                mod = import_module(module)
#                callback = getattr(mod, attr)
#                callback_r = callback(request, m)#

#            if callback_r or (request.user not in m.users.all() and m.expire_on_view is True) or m.to == 'ALL' or (m.to == 'AUTH' and request.user.is_authenticated()) or m.to == request.user.username or m.to in request.user.groups.all():
#                messages.append({'mtype': m.mtype, 'message': m.message})
#            if m.expire_on_view:
#                m.users.add(request.user)
#                m.save()#

#        return {'messages': messages}
#    except Exception, e:
#        pass
#    return {'messages': []}


