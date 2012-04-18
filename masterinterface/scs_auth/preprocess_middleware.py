from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import logout , login
from tktauth import validateTicket, createTicket
from datetime import datetime
import binascii

class MultiHostMiddleware:

    def process_view(self, request, callback, callback_args, callback_kwargs):

        request.META['NEW_VPH_TKT_COOKIE']=False

        try:

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

            if  request.COOKIES.get('vph-tkt'):

                ticket=binascii.a2b_base64(request.COOKIES['vph-tkt'])

                if validateTicket(settings.SECRET_KEY,ticket) is None:
                    logout(request)
                request.META['VPH_TKT_COOKIE'] = ticket
            else:
                if request.user.is_authenticated() and not request.user.username == 'admin':
                    logout(request)


            if request.GET.get('ticket'):
                try:
                    ticket = binascii.a2b_base64(request.GET['ticket'])
                except :
                    return
                user_data = validateTicket(settings.SECRET_KEY,ticket)
                if  user_data is not None :

                    # user_key =  ['language', 'country', 'postcode', 'fullname', 'nickname', 'email']
                    user_key =  ['nickname', 'fullname', 'email', 'language', 'country', 'postcode']
                    user_value=user_data[3]
                    user_dict={}

                    for i in range(0, len(user_key)):
                        user_dict[user_key[i]]=user_value[i]


                    new_user = RemoteUserBackend()
                    user = new_user.authenticate( user_dict['nickname'] )

                    user.backend ='django.contrib.auth.backends.RemoteUserBackend'
                    user.first_name = user_dict['fullname'].split(" ")[0]
                    user.last_name =  user_dict['fullname'].split(" ")[1]
                    user.email = user_dict['email']
                    user.last_login = str(datetime.now())

                    user.save()

                    login(request,user)
                    request.META['NEW_VPH_TKT_COOKIE'] = True
                    request.META['TKT_TOKEN'] = user_data[2]
                    request.META['TKT_USER_DATA'] = user_value

        except KeyError:
            pass # use default urlconf (settings.ROOT_URLCONF)



    def process_response(self, request, response):

        if request.META.get('NEW_VPH_TKT_COOKIE'):

            new_tkt = createTicket(
                settings.SECRET_KEY,
                request.user.username,
                tokens= request.META['TKT_TOKEN'],
                user_data = request.META['TKT_USER_DATA']
            )

            tkt64 = binascii.b2a_base64(new_tkt).rstrip()

            response.set_cookie( 'vph-tkt', tkt64 )


        if request.META.get("VPH_TKT_COOKIE") is None:
            return response

        if not request.user.is_authenticated():
            response.delete_cookie('vph-tkt')
            return response
        ticket=binascii.a2b_base64(request.COOKIES['vph-tkt'])
        data = validateTicket(settings.SECRET_KEY,ticket)
        if data is not None:
            (digest, userid, tokens, user_data, timestamp) = data
            tkt64 =binascii.b2a_base64(createTicket(settings.SECRET_KEY, userid, tokens, user_data))
            response.set_cookie( 'vph-tkt', tkt64 )

            return response

        return response

