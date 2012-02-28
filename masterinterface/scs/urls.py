from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^$', 'home'),
    url(r'^done/$', 'done'),
    url(r'^error/$', 'error'),
    url(r'^logout/$','logout'),
    url(r'^bt_login/$', 'bt_login'),
    url(r'^test/$', 'test'),
)
