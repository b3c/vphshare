from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^$', 'home'),
    url(r'^login/$', 'login'),
    url(r'^profile/$', 'profile'),
    url(r'^login-error/$', 'login_error'),
    url(r'^logout/$','logout'),
    url(r'^bt_login/$', 'bt_login'),
    url(r'^bt_loginform/$', 'bt_loginform'),
    url(r'^services/$', 'services'),
    url(r'^test/$', 'test'),
    url(r'^done/$', 'done'),
)
