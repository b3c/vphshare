from django.conf.urls import patterns, url
from django.contrib import admin
from masterinterface.scs_workflows.views import *
admin.autodiscover()

urlpatterns = patterns(
    'scs_workflows.views',
    url(r'^workflows/$', workflowsView, name='workflows'),
    url(r'^workflows/new/$', create_workflow, name='createWorkflows'),
    url(r'^workflows/edit/(?P<id>\d+)/$', edit_workflow, name='editWorkflow'),
    )

