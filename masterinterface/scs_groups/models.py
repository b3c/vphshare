__author__ = "Matteo Balasso (m.balasso@scsitaly.com)"

from django.db import models
from django.contrib.auth.models import Group, User


class VPHShareSmartGroup(Group):

    managers = models.ManyToManyField(User)
    parent = models.ForeignKey(Group, related_name='+', blank=True, null=True)
    active = models.BooleanField(blank=False, default=True)

    class Meta:
        verbose_name_plural = "VPHShareSmartGroups"
        ordering = ['name']
        permissions = (
            ('can_add_user_to_smartgroup', 'Can add user to smartgroup'),
            ('can_remove_user_from_smartgroup', 'Can remove user from smartgroup'),
            ('can_add_smartgroup', 'Can add smartgroup'),
            ('can_delete_smartgroup', 'Can delete smartgroup'),
        )

    def __unicode__(self):
        return self.name

    def remove_users(self, users=[]):
        if len(users):
            for user in users:
                self.user_set.remove(user)
        else:
            # TODO optimize this cycle with a sql statement
            for user in self.user_set.all():
                self.user_set.remove(user)


class Institution(Group):

    description = models.CharField(max_length=255, blank=False, help_text='Institution description')
    address = models.CharField(max_length=64, blank=False, help_text='Address')
    country = models.CharField(max_length=64, blank=False, help_text='Country')
    logo = models.ImageField(blank=True, help_text='Institution logo image', upload_to='logos')

    signed_dsa = models.BooleanField(blank=False, help_text='Indicating that has signed Data-Sharing Agreement introducing Institutional policies')
    policies_url = models.URLField(max_length=255, blank=True, help_text='Link to where Institutional Policy documents are available')

    admin_fullname = models.CharField(max_length=64, blank=False, help_text='Administration contact person fullname')
    admin_address = models.CharField(max_length=1024, blank=False, help_text='Administration contact address')
    admin_phone = models.CharField(max_length=64, blank=False, help_text='Administration contact phone number')
    admin_email = models.EmailField(max_length=64, blank=False, help_text='Administration contact email')

    formal_fullname = models.CharField(max_length=64, blank=True, help_text='Formal contact person fullname -legally responsible person')
    formal_address = models.CharField(max_length=1024, blank=True, help_text='Formal contact address')
    formal_phone = models.CharField(max_length=64, blank=True, help_text='Formal contact phone number')
    formal_email = models.EmailField(max_length=64, blank=True, help_text='Formal contact email')

    breach_fullname = models.CharField(max_length=64, blank=True, help_text='Breach contact person fullname - person to be notified in case of breach of security, privacy detected or suspected')
    breach_address = models.CharField(max_length=1024, blank=True, help_text='Breach contact address')
    breach_phone = models.CharField(max_length=64, blank=True, help_text='Breach contact phone number')
    breach_email = models.EmailField(max_length=64, blank=True, help_text='Breach contact email')

    managers = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = "Institutions"
        ordering = ['name']
        permissions = (
            ('can_add_user_to_institution', 'Can add user to Institution'),
        )

    def __unicode__(self):
        return self.name


class Study(Group):

    title = models.CharField(max_length=255, blank=False, help_text='Study title')
    description = models.CharField(max_length=255, blank=False, help_text='Study description')

    start_date = models.DateField(blank=False, help_text='Study start date')
    finish_date = models.DateField(blank=False, help_text='Study finish date')

    institution = models.ForeignKey(Institution)

    principals = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = "Studies"
        ordering = ['name']
        permissions = (
            ('can_add_user_to_study', 'Can add user to Study'),
        )

    def __unicode__(self):
        return self.name


class AuditLog(models.Model):

    date = models.DateField(auto_now=True, blank=False)
    log = models.CharField(max_length=512, blank=False)

    def __unicode__(self):
        return "%s - %s - %s" % (self.id, self.date.toordinal(), self.log)


class SubscriptionRequest(models.Model):

    user = models.ForeignKey(User, blank=False)
    group = models.ForeignKey(Group, blank=False)
    date = models.DateField(auto_now=True, blank=False)

    def __unicode__(self):
        return "%s - %s" % (self.user.username, self.group.name)
