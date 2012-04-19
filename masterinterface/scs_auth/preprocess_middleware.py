from django.contrib.auth import logout , login
from django.contrib.auth import authenticate
import binascii

class MultiHostMiddleware:

    def process_view(self, request, callback, callback_args, callback_kwargs):

        request.META['NEW_VPH_TKT_COOKIE']=False

        try:

            ##QUESTA E' DA SISTEMARE CON LA PIPELINE
            if request.session._session.get('_auth_user_backend'):
                if request.session._session['_auth_user_backend'] == 'scs_auth.backends.biomedtown.BiomedTownBackend' and request.user.is_authenticated():
                    """
                    """

                    #### IS NOT A FINAL IMPLEMENTATION ONLY FOR DEVELOPER
                    if request.user.username=='mi_testuser':
                        tokens=[]
                    else:
                        tokens=['developer']
                    #######

                    user_value = [ request.user.username, '%s %s' % (request.user.first_name, request.user.last_name), request.user.email, '', '', '']
                    request.META['NEW_VPH_TKT_COOKIE'] = True
                    request.META['TKT_TOKEN'] = tokens
                    request.META['TKT_USER_DATA'] = user_value
                    return
            ######

            if  request.COOKIES.get('vph-tkt'):

                user, tkt64 = authenticate(ticket=request.COOKIES['vph-tkt'])

                if user is None:
                    logout(request)

                request.META['VPH_TKT_COOKIE'] = tkt64

            else:

                if request.user.is_authenticated() and not request.user.username == 'admin':
                    logout(request)


            if request.GET.get('ticket') and not request.path.count('validatetkt'):
                try:
                    ticket = binascii.a2b_base64(request.GET['ticket'])
                except :
                    return

                user, tkt64 = authenticate(ticket=request.GET['ticket'])

                if  user is not None :

                    login(request,user)

                    request.META['VPH_TKT_COOKIE'] = tkt64


        except KeyError:
            pass # use default urlconf (settings.ROOT_URLCONF)



    def process_response(self, request, response):

        if request.META.get("VPH_TKT_COOKIE") is None:
            return response

        if not request.user.is_authenticated():
            response.delete_cookie('vph-tkt')
            return response

        response.set_cookie( 'vph-tkt', request.META['VPH_TKT_COOKIE'])

        return response

