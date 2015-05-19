from django.conf import settings
from masterinterface.scs_groups.models import InstitutionPortal
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

class institutionPortaleMiddleware(object):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        try:
            #if request.user.is_authenticated():
            subdomain = request.META['HTTP_HOST'].split(settings.SESSION_COOKIE_DOMAIN)[0]
            if subdomain not in ['portal','devel'] and request.META['HTTP_HOST'] not in settings.BASE_URL: # we are in a institutional portal
                institutionportal = InstitutionPortal.objects.get(subdomain=subdomain)
                request.session['institutionportal'] = institutionportal
            else:
                if request.session.get('institutionportal', None):
                    del(request.session['institutionportal'])
        except Exception:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            if request.session.get('institutionportal', None):
                del(request.session['institutionportal'])
            pass

    def process_response(self, request, response):
        try:
            if isinstance(response,HttpResponsePermanentRedirect):
                return response
            subdomain = request.META['HTTP_HOST'].split(settings.SESSION_COOKIE_DOMAIN)[0]
            if subdomain not in ['portal','devel'] and request.META['HTTP_HOST'] not in settings.BASE_URL: # we are in a institutional portal
                institutionportal = InstitutionPortal.objects.get(subdomain=subdomain)
                request.session['institutionportal'] = institutionportal
                if all(x not in request.path for x in ['login', 'done', 'scs_auth', 'media', 'static', 'api']) and request.user not in institutionportal.institution.user_set.all():
                    if request.user.is_anonymous() and request.path not in ['/','']:
                        request.session['errormessage'] = "Please login to access to the requested resource"
                        if request.path not in ['/','']:
                            return render_to_response("scs/login.html", {}, RequestContext(request))
                    else:
                        if request.path not in ['/','']:
                            request.session['errormessage'] = "You can't access if you are not memeber of the %s institution group" %institutionportal.institution.name
                            return render_to_response("scs/403.html", {}, RequestContext(request))

            else:
                if request.session.get('institutionportal', None):
                    del(request.session['institutionportal'])
            return response
        except Exception, e:
            print e
            print request.META['HTTP_HOST']
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            if request.session.get('institutionportal', None):
                del(request.session['institutionportal'])
            return HttpResponsePermanentRedirect(settings.BASE_URL)
