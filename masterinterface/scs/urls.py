from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'scs.views',
    url(r'^$', 'home'),
    url(r'^login/$', 'login'),
    url(r'^contacts/$', 'contacts'),
    url(r'^help/$', 'help'),
    url(r'^profile/$', 'profile'),
    url(r'^login-error/$', 'login_error'),
    url(r'^services/$', 'services'),
    url(r'^workflows/$', 'workflows'),
    url(r'^test/$', 'test'),
    url(r'^users_admin/$', 'user_access_admin'),
)
