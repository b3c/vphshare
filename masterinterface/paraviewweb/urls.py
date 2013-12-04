from django.conf.urls import patterns, url, include
from django.contrib import admin
from masterinterface.paraviewweb.views import *
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    'paraviewweb.views',
    url(r'^pvw_start_session$', 'pvw_start_session', name='pvw_start_session' ),
    url(r'^pvw_close_session$', 'pvw_close_session', name='pvw_close_session' ),
    url(r'^pvw_method_call$', 'pvw_method_call', name='pvw_method_call' ),
    url(r'^pvw_method_call/$', 'pvw_method_call', name='pvw_method_call' ),
    url(r'^slice/$', TemplateView.as_view(template_name='paraviewweb/slice.html')),
    url(r'^volume/$', TemplateView.as_view(template_name='paraviewweb/volume.html')),
    url(r'^surface/$', TemplateView.as_view(template_name='paraviewweb/surface.html')),
    url(r'^$', TemplateView.as_view(template_name='paraviewweb/embed.html')),

)