from django.conf import settings
from masterinterface.scs_groups.models import InstitutionPortal
from masterinterface.scs.views import page403
from django.http import HttpResponsePermanentRedirect

class institutionPortaleMiddleware(object):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        try:
            if request.user.is_authenticated():
                subdomain = request.META['HTTP_HOST'].split(settings.SESSION_COOKIE_DOMAIN)[0]
                if subdomain != 'portal': # we are in a institutional portal
                    institutionportal = InstitutionPortal.objects.get(subdomain=subdomain)
                    request.session['institutionportal'] = institutionportal
                else:
                    if request.session.get('institutionportal', None):
                        del(request.session['institutionportal'])
        except Exception:
            if request.session.get('institutionportal', None):
                del(request.session['institutionportal'])
            pass

    def process_response(self, request, response):
        try:
            subdomain = request.META['HTTP_HOST'].split(settings.SESSION_COOKIE_DOMAIN)[0]
            if subdomain != 'portal': # we are in a institutional portal
                institutionportal = InstitutionPortal.objects.get(subdomain=subdomain)
                request.session['institutionportal'] = institutionportal
                if request.user not in institutionportal.institution.user_set.all():
                    request.session['errormessage'] = "You can't access if you are not memeber of the %s institution group" %institutionportal.institution.name
                    return page403(request)
            else:
                if request.session.get('institutionportal', None):
                    del(request.session['institutionportal'])
            return response
        except Exception, e:
            if request.session.get('institutionportal', None):
                del(request.session['institutionportal'])
            return HttpResponsePermanentRedirect(settings.BASE_URL)
