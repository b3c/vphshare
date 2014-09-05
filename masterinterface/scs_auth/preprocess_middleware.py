from django.contrib.auth import logout , login
from auth import authenticate
import binascii


class masterInterfaceMiddleware(object):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Proces_view work before view rendering. Verify usere's ticket (from cookie or ticket attribute)
        """
        request.META['NEW_VPH_TKT_COOKIE'] = False

        try:
            #FROM COOKIE
            #Check user's cookie  if validate ticket is ok, update ticket timestamp else session expire.
            if  request.COOKIES.get('vph-tkt'):
                try:
                    client_address = request.META['REMOTE_ADDR']
                    user, tkt64 = authenticate(ticket=request.COOKIES['vph-tkt'], cip=client_address)
                except:
                    logout(request)
                    request.META['VPH_TKT_COOKIE'] = True
                    request.ticket = None
                    return

                if user is None:
                    logout(request)
                    request.META['VPH_TKT_COOKIE'] = True
                    request.ticket = None
                    return
                request.ticket = tkt64
                request.META['VPH_TKT_COOKIE'] = tkt64

            else:

                if request.user.is_authenticated() and not request.user.username == 'admin':
                    logout(request)
                    request.ticket = None
                    request.META['VPH_TKT_COOKIE'] = True
                    return

            #FROM GET ATTRIBUTE
            #if validate ticket is ok, open new session and set ticket cookie only for super user , not avlid under api.

            if request.GET.get('ticket') and not request.path.count('api') and request.user.is_superuser:
                try:
                    ticket = binascii.a2b_base64(request.GET['ticket'])
                except :
                    return
                user, tkt64 = authenticate(ticket=request.GET['ticket'])
                if  user is not None :
                    login(request,user)
                    request.META['VPH_TKT_COOKIE'] = tkt64

        except KeyError:
            pass  # use default urlconf (settings.ROOT_URLCONF)

    def process_response(self, request, response):
        """
        Process_response work after view rendering.
        Set/update ticket cookie if necessary.
        """

        if request.META.get("VPH_TKT_COOKIE") is None:
            return response

        if not request.user.is_authenticated():
            response.delete_cookie('vph-tkt')
            return response

        response.set_cookie('vph-tkt', request.META['VPH_TKT_COOKIE'])

        return response


