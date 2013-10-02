__author__ = 'Alfredo Saglimbeni <a.saglimbeni@scsitaly.com>'

import json
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from piston.handler import BaseHandler
from masterinterface.scs_auth.auth import authenticate
from masterinterface.scs.models import message as messageModel
from django.core.mail import EmailMultiAlternatives
from django.template import loader


class NotifyException(Exception):
    """
    called when recipient doesn't valid or doesn't exist
    """


def alert_user_by_email(mail_from, mail_to, subject, mail_template, dictionary={}):
    """
        send an email to alert user
    """

    text_content = loader.render_to_string('scs/%s.txt' % mail_template, dictionary=dictionary)
    html_content = loader.render_to_string('scs/%s.html' % mail_template, dictionary=dictionary)
    msg = EmailMultiAlternatives(subject, text_content, mail_from, [mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.content_subtype = "html"
    msg.send()


class Notify(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
    """

    def read(self, request, ticket, recipient, message, subject=''):
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
                        recipient = request.GET['recipient'] if request.GET.get('recipient') else recipient = None
                        message = request.GET['message'] if request.GET.get('message') else recipient = None
                        subject = request.GET['subject'] if request.GET.get('subject') else recipient = None

                        if recipient is None:
                            raise NotifyException('Recipient is wrong')
                        elif message is None or message == '':
                            raise NotifyException('Message is empty')

                        try:
                            user = User.objects.get(username=recipient)

                            messageModel(recipient=User, message=message, subject=subject)

                            alert_user_by_email(
                                'webmaster@vph-share.eu',
                                user.email,
                                subject,
                                'notify',
                                {
                                    message:message,
                                    recipient: recipient
                                }
                            )

                        except ObjectDoesNotExist:
                            try:
                                group = Group.objects.get(name=recipient)
                                for user in group.user_set.all():
                                    messageModel(recipient=User, message=message, subject=subject)
                                    alert_user_by_email(
                                        'webmaster@vph-share.eu',
                                        user.email,
                                        subject,
                                        'notify',
                                        {
                                            message: message,
                                            recipient: recipient
                                        }
                                    )
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
