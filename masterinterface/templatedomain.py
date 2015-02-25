from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from masterinterface.scs_groups.models import Institution

def domainx(request):
    '''
    A context processor to add the "GROUP SUBDOMAIN" to the current Context
    '''

    return {'institutionportal':request.session.get('institutionportal', None), 'settings':settings}
