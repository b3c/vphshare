from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import scsWorkflowForm, scsWorkflow
import requests
import re
import os
import xmltodict
from masterinterface.atos.metadata_connector import *

@login_required
def workflowsView(request):

    workflows = []

    try:
        dbWorkflows = scsWorkflow.objects.all()
        for workflow in dbWorkflows:
            workflow.metadata = get_resource_metadata(workflow.metadataId)
            workflows.append(workflow)

    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs_workflows/workflows.html", {'workflows': workflows}, RequestContext(request))


@login_required
def edit_workflow(request, id=False):
    try:
        if id:
            dbWorkflow = scsWorkflow.objects.get(id=id)
            if request.user != dbWorkflow.user:
                raise

            metadata = get_resource_metadata(dbWorkflow.metadataId)
            metadata['title'] = metadata['name']
            form = scsWorkflowForm(metadata, instance=dbWorkflow)

        if request.method == "POST":
            form = scsWorkflowForm(request.POST, request.FILES, instance=dbWorkflow)

            if form.is_valid():
                workflow = form.save(commit=False)
                workflow.user = request.user

                metadata_payload = {'name': form.data['title'], 'description': form.data['description'],
                                    'author': request.user.username, 'category': form.data['category'],
                                    'tags': form.data['tags'], 'type': 'Workflow',
                                    'semantic_annotations': form.data['semantic_annotations'],
                                    'licence': form.data['licence'], 'local_id': workflow.id}

                update_resource_metadata(dbWorkflow.metadataId, metadata_payload)

                workflow.save()
                request.session['statusmessage'] = 'Changes were successful'
                return redirect('/workflows')

        return render_to_response("scs_workflows/workflows.html",
                                  {'form': form},
                                  RequestContext(request))
    except AtosServiceException, e:
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_workflows/workflows.html",
                                  {'form': form},
                                  RequestContext(request))

    except Exception, e:
        if not request.session['errormessage']:
            request.session['errormessage'] = 'Some errors occurs, please try later. '
        return redirect('/workflows')



@login_required
def create_workflow(request):
    try:
        form = scsWorkflowForm()
        if request.method == 'POST':
            form = scsWorkflowForm(request.POST, request.FILES)

            if form.is_valid():
                workflow = form.save(commit=False)

                #validate filetype
                filename = workflow.t2flow.path
                ext = os.path.splitext(filename)[1]
                ext = ext.lower()
                if ext != '.t2flow':
                    request.session['errormessage'] = "Taverna workflow need a correct file type, es. *.t2flow."
                    raise
                filename = workflow.xml.path
                ext = os.path.splitext(filename)[1]
                ext = ext.lower()
                if ext != u'.xml':
                    request.session['errormessage'] = "Input definition file need an xml file type"
                    raise

                workflow.user = request.user
                workflow.save()
                metadata_payload = {'name': form.data['title'], 'description': form.data['description'],
                                    'author': request.user.username, 'category': form.data['category'],
                                    'tags': form.data['tags'], 'type': 'Workflow',
                                    'semantic_annotations': form.data['semantic_annotations'],
                                    'licence': form.data['licence'], 'local_id': workflow.id}

                global_id = set_resource_metadata(metadata_payload)

                workflow.metadataId = global_id
                workflow.save()

                request.session['statusmessage'] = 'Workflow successfully created'
                return redirect('/workflows')
            else:
                request.session['errormessage'] = 'Some fields are wrong or missed.'
                return render_to_response("scs_workflows/workflows.html", {'form': form}, RequestContext(request))
        raise

    except AtosServiceException, e:
        if workflow is not None:
            workflow.delete()
        request.session['errormessage'] = 'Metadata service not work, please try later.'
        return render_to_response("scs_workflows/workflows.html", {'form': form}, RequestContext(request))

    except Exception, e:
        return render_to_response("scs_workflows/workflows.html", {'form': form}, RequestContext(request))
