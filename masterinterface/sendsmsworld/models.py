from django.db import models
from django.utils.translation import ugettext_lazy as _
from masterinterface.scs.config import CharField_max_length

# Create your models here.

class sendSMS( models.Model):
    FromEmailAddress = models.CharField( _('FromEmailAddress'), null=False, max_length=CharField_max_length)
    CountryCode = models.CharField( _('CountryCode'), null=False, max_length=CharField_max_length)
    MobileNumber = models.CharField( _('MobileNumber'), null=False, max_length=CharField_max_length)
    Message = models.CharField( _('Message'), null=False, max_length=CharField_max_length)

class sendSMSResponse( models.Model):
    sendSMSResult = models.CharField( _('sendSMSResult'), null=False, max_length=CharField_max_length)
