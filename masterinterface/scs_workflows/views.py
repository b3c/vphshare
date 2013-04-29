from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .models import scsWorkflowForm, scsWorkflow
import requests
import re
import os
import xmltodict

PAYLOAD = """
    <metadata>
    <type>Workflow</type>
    <name>%s</name>
    <description>%s</description>
    <author>%s</author>
    <category>%s</category>
    <tags>%s</tags>
    <semantic_annotations>%s</semantic_annotations>
    <licence>%s</licence>
    <rating>0</rating>
    <views>0</views>
    <local_id>%s</local_id>
    </metadata>"""

@login_required
def workflowsView(request):

    try:
        dbWorkflows = scsWorkflow.objects.all()
        workflows = []
        key = 0
        for workflow in dbWorkflows:
            response = requests.get('http://vphshare.atosresearch.eu/metadata-retrieval/rest/metadata/%s' % workflow.metadataId)
            workflow.metadata = xmltodict.parse(response.text.encode())
            workflow.key = key
            key += 1
            workflows.append(workflow)
    except Exception, e:
        request.session['errormessage'] = 'Metadata server is down. Please try later'
        pass

    return render_to_response("scs_workflows/workflows.html",
                              {'workflows': workflows},
                              RequestContext(request))


@login_required
def edit_workflow(request, id=False):
    try:
        if id:
            dbWorkflow = scsWorkflow.objects.get(id=id)
            if request.user != dbWorkflow.user:
                raise
            response = requests.get('http://vphshare.atosresearch.eu/metadata-retrieval/rest/metadata/%s' % dbWorkflow.metadataId)
            metadata = xmltodict.parse(response.text.encode())['resource_metadata']
            metadata['title'] = metadata['name']
            form = scsWorkflowForm(metadata, instance=dbWorkflow)

        if request.method == "POST":
            form = scsWorkflowForm(request.POST, request.FILES, instance=dbWorkflow)

            if form.is_valid():
                workflow = form.save(commit=False)
                workflow.user = request.user
                workflow.save()
                name = form.data['title']
                description = form.data['description']
                author = request.user.username
                category = form.data['category']
                tags = form.data['tags']
                semantic_annotations = form.data['semantic_annotations']
                licence = form.data['licence']
                local_id = workflow.id
                headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
                data = PAYLOAD % (name,description, author, category, tags, semantic_annotations, licence, local_id)
                response = requests.put('http://vphshare.atosresearch.eu/metadata-retrieval/rest/metadata/%s' % dbWorkflow.metadataId, data,
                                         headers=headers)

                request.session['statusmessage'] = 'Changes were successful'
                return redirect('/workflows')

        return render_to_response("scs_workflows/workflows.html",
                                  {'form': form},
                                  RequestContext(request))
    except Exception, e:
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
                name = form.data['title']
                description = form.data['description']
                author = request.user.username
                category = form.data['category']
                tags = form.data['tags']
                semantic_annotations = form.data['semantic_annotations']
                licence = form.data['licence']
                local_id = workflow.id
                headers = {'Accept': '*/*', 'content-type': 'application/xml', 'Cache-Control': 'no-cache'}
                data = PAYLOAD % (name,description, author, category, tags, semantic_annotations, licence, local_id)
                response = requests.post('http://vphshare.atosresearch.eu/metadata-retrieval/rest/metadata', data,
                                         headers=headers)

                regEx = re.compile('global_id>(.*?)<')
                globalId = regEx.search(response.text).group(1)

                workflow.metadataId = globalId
                workflow.save()

                request.session['statusmessage'] = 'Workflow successfully created'
                return redirect('/workflows')
            else:
                request.session['errormessage'] = 'Some fields are wrong or missed.'
                return render_to_response("scs_workflows/workflows.html",
                                          {'form': form},
                                          RequestContext(request))
        raise
    except Exception, e :
        return render_to_response("scs_workflows/workflows.html",
                              {'form': form},
                              RequestContext(request))
