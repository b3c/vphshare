from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .models import scsWorkflowForm

@login_required
def workflows(request):
    return render_to_response("scs_workflows/workflows.html",
                              {},
                              RequestContext(request))
@login_required
def create_workflow(request):
    form = scsWorkflowForm()
    return render_to_response("scs_workflows/workflows.html",
                              {'form': form},
                              RequestContext(request))
