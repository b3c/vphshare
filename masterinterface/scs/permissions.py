
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator as guard

from functools import wraps
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import  available_attrs

def check_sample_permission(f):
    """ Function decorator mock up
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated

def is_staff():
    """ Function decorator mock up
    """

    def decorated(f):
        def inner (request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated():
                return render_to_response('scs/no_permission.html',
                    context_instance=RequestContext(request)
                )
            if user.is_staff:
                return f(request, *args, **kwargs)
            return render_to_response('scs/no_permission.html',
                context_instance=RequestContext(request)
            )
        return wraps(f, assigned=available_attrs(f))(inner)
    return decorated