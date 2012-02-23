# Create your views here.
# Create your views here.
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext
from forms import sendSMSForm
from models import sendSMS as sendSMSRequestType
from models import sendSMSResponse as sendSMSResponseType
from masterinterface.scs.services import invokeSoapService
from masterinterface.scs.permissions import checkSamplePermission