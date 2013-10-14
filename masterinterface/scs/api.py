__author__ = 'Alfredo Saglimbeni <a.saglimbeni@scsitaly.com>'

import json
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs.models import Notification


class NotifyException(Exception):
    """
    called when recipient doesn't valid or doesn't exist
    """


class Notify(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request):
        """
            Notifycation message service.
            At the service invocation:
            - check the sender ticket validity
            - send an email to the recipient(s) from webmaster@vph-share.eu with the given text and subject (if provided).
            - when the receiver will login into the MI, a popup message will be shown in the homepage. The user will be
            able to hide the message by clicking the "X" control on the message itself.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : the ticket of the sender base 64 ticket.
            recipient: the username of the receiver (or the group id if you want to notify a group of users)
            message: the message body (plain text)
            subject: the message subject [optional]

            Return:

            Successes - status message 200
            Failure - 400 error with message
            Failure - 403 error when ticket is not valid.

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:
                    try:

                        if request.GET.get('recipient', None):
                            recipient = request.GET['recipient']
                        else:
                            recipient = None
                        if request.GET.get('message', None):
                            message = request.GET['message']
                        else:
                            message = None
                        if request.GET.get('subject', None):
                            subject = request.GET['subject']
                        else:
                            subject = ''

                        if recipient is None:
                            raise NotifyException('Recipient is wrong')
                        elif message is None or message == '':
                            raise NotifyException('Message is empty')

                        try:
                            user = User.objects.get(username=recipient)

                            n = Notification(recipient=user, message=message, subject=subject).save()

                        except ObjectDoesNotExist:
                            try:
                                group = Group.objects.get(name=recipient)
                                for user in group.user_set.all():
                                    Notification(recipient=user, message=message, subject=subject).save()
                                pass
                            except ObjectDoesNotExist:
                                raise NotifyException('recipient is wrong')

                        response = HttpResponse(status=200)
                        response._is_string = True
                        return response

                    except NotifyException, e:
                        response = HttpResponse(status=400, content=e)
                        response._is_string = True
                        return response
                else:
                    raise Exception

        except Exception, e:
            response = HttpResponse(status=403)
            response._is_string = True
            return response
