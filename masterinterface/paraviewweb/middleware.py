__author__ = 'alfredo Saglimbeni'

from .models import ParaviewInstance
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os

class paraviewWebMiddleware:

    def process_view(self, request, callback, callback_args, callback_kwargs):

            if request.user.is_authenticated():
                try:
                    pvw_instance = ParaviewInstance.objects.get(user=request.user, deletion_time__exact=None)
                    if (datetime.utcnow() - pvw_instance.creation_time.replace(tzinfo=None)).seconds >= settings.PARAVIEWWEB_SERVER_TIMEOUT:
                        try:
                            if request.session[str(pvw_instance.pid)].poll() is None:
                                request.session[str(pvw_instance.pid)].kill()
                                request.session[str(pvw_instance.pid)].wait()
                        except Exception, e:
                            pass
                        pvw_instance.deletion_time = datetime.now()
                        pvw_instance.save()
                except ObjectDoesNotExist:
                    pass
