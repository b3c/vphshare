

def statusMessage(request):
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
