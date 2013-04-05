from django.conf.urls.defaults import patterns, include, url
#from django.shortcuts import render_to_response

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vphshare.views.home', name='home'),
    # url(r'^vphshare/', include('vphshare.foo.urls')),

    # admin/doc urls
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # admin urls
    url(r'^admin/', include(admin.site.urls)),

    # authentication
    url(r'', include('social_auth.urls')),

    # favicon
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),

    # cyfronet
    url(r'^cyfronet/', include('masterinterface.cyfronet.urls')),

    # groups
    url(r'^groups/', include('masterinterface.scs_groups.urls')),
    url(r'^api/', include('masterinterface.scs_groups.apiurls')),

    # security
    url(r'^security/', include('masterinterface.scs_security.urls')),

    # default roolback
    url(r'', include('masterinterface.scs.urls')),
    url(r'^scs/', include('masterinterface.scs.urls')),
    url(r'', include('masterinterface.scs_auth.urls')),
    url(r'scs_auth/', include('masterinterface.scs_auth.urls')),
    url(r'', include('masterinterface.scs_search.urls'))

    ##NEW_URL
)
