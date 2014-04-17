from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from raven.contrib.django.raven_compat.models import client


class Notification(models.Model):

    recipient = models.ForeignKey(User)
    message = models.CharField(null=False, blank=False, max_length=350)
    subject = models.CharField(null=True, blank=True,  max_length=90, default='')
    hidden = models.BooleanField(null=False, default=False)

    def __unicode__(self):
        return unicode(self.pk)+u' - '+unicode(self.recipient.username)


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


def notification_created(sender, instance, created, **kwargs):
    try:
        if created:
            alert_user_by_email(
                'webmaster@vph-share.eu',
                instance.recipient.email,
                'VPH-Share notification delivery',
                'notify',
                {
                    'subject': instance.subject,
                    'message': instance.message,
                    'recipient': instance.recipient
                }
            )
    except Exception, e:
        client.captureException()
        pass

post_save.connect(notification_created, Notification)

