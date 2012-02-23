from django.conf.urls.defaults import patterns, url, include

from views import sendSMS

urlpatterns = patterns('sendsmsworld.views',
    url(r'^sendSMS/', sendSMS.as_view() ),
)
