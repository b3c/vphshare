from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from masterinterface.scs.views import page403, page404, page500
from django.forms.models import model_to_dict
import models as M

import json
import itertools

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def ejobs_view_get(request):
    if request.user.is_authenticated():
        try:
            objs = M.ejob_get_gte_one(request.user.id,request.user.id)
            return render_to_response(
                    'cilab_ejobs/ejobs_view_get.html',
                    { "ejobs": objs },
                    RequestContext(request)
                    )
        except:
            page403(request)

@login_required
@csrf_exempt
def ejobs_view_delete(request):
    if request.user.is_authenticated() and request.method == 'POST' and 'job_id' in request.POST:
        try:
            job_id = request.POST["job_id"]
            ej = M.ejob_cancel(job_id,request.user.id)

            return HttpResponse(status=200,
                    content=json.dumps(model_to_dict(ej), sort_keys=False),
                    content_type='application/json')
        except Exception, e:
            return HttpResponse(status=500,
                    content=json.dumps(
                        { "exception":"%s" % (str(e),) },
                        sort_keys=False
                        ),
                    content_type='application/json')

