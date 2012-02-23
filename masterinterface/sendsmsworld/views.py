# Create your views here.
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.template import RequestContext
from forms import sendSMSForm
from models import sendSMS as sendSMSRequestType
from models import sendSMSResponse as sendSMSResponseType
from masterinterface.scs.services import invokeSoapService
from masterinterface.scs.permissions import checkSamplePermission


class sendSMS(View):

    # set the template name
    template_name = 'sendsmsworld/sendSMS.html'
    action_url = '/sendsmsworld/sendSMS/'
    wsdl_url = 'http://www.webservicex.net/sendsmsworld.asmx?WSDL'
    method = 'sendSMS'
    service = 'SendSMSWorld'
    port = 'SendSMSWorldSoap'
    requestType = sendSMSRequestType
    responseType = sendSMSResponseType

    def get(self, request):
        """ get the form page to send the request """

        form = sendSMSForm()

        return render_to_response(
                    self.template_name,
                    { 'title':'sendSMS form',
                      'form' : form,
                      'action': self.action_url,
                      'results': None},
                    context_instance=RequestContext(request)
        )

    # your permission control goes here
    @checkSamplePermission
    def post(self, request):
        """ validate form and post request to the service """

        # check form validation
        form = sendSMSForm( request.POST, request.FILES)

        if form.is_valid():

            # invoke service
            result = invokeSoapService(
                self.wsdl_url,
                self.service,
                self.port,
                self.method,
                form.cleaned_data,
                self.requestType,
                self.responseType
            )

            return render_to_response(
                self.template_name,
                { 'title':'sendSMS form',
                  'form' : sendSMSForm(),
                  'action': self.action_url,
                  'statusmessage': 'Action Performed',
                  'result': result},
                context_instance=RequestContext(request)
            )


        # form validation failed
        errormessage = 'Error while validating form'

        return render_to_response(
            self.template_name,
                { 'title':'sendSMS form',
                  'form' : sendSMSForm(),
                  'action': self.action_url,
                  'errormessage': errormessage,
                  'results': None},
            context_instance=RequestContext(request)
        )





