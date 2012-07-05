from django.conf.urls import patterns, url, include
from django.contrib import admin
from masterinterface.scs.views import *
admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^$', 'home' ),
    url(r'^login/$', login , name='login'),
    url(r'^contacts/$', contacts ,  name='contacts'),
    url(r'^help/$', help ,  name='help'),
    url(r'^profile/$',profile, name='profile'),
    url(r'^login-error/$', login_error , name='login_error'),
    url(r'^services/$', services ,name='services'),
    url(r'^workflows/$', workflows , name='workflows'),
    url(r'^test/$', test , name='test'),
    url(r'^users_admin/$', users_access_admin , name='users_access_admin'),
)

