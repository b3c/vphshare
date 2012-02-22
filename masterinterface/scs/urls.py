from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

from masterinterface.scs.views import home, done, logout, error, form

admin.autodiscover()
urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^done/$', done, name='done'),
    url(r'^error/$', error, name='error'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^form/$', form, name='form'),
)
