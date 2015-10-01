__author__ = "Matteo Balasso (m.balasso@scsitaly.com)"

from django.db import models
from django.contrib.auth.models import Group, User

class VPHShareSmartGroup(Group):

    managers = models.ManyToManyField(User)
    parent = models.ForeignKey(Group, related_name='+', blank=True, null=True)
    active = models.BooleanField(blank=False, default=True)
    description = models.CharField(max_length=255, blank=True)

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

    def get_ancestors(self):
        ancestors = []
        if self.parent:
            parent = self.parent.vphsharesmartgroup
            while parent is not None:
                if parent.active:
                    ancestors.append(parent)
                parent = parent.parent.vphsharesmartgroup

        return ancestors

    def remove_users(self, users=[]):
        # if users is given remove the listo of user from the group membership
        if len(users):
            for user in users:
                self.user_set.remove(user)
        else:
            # defaul behaivor remove all users from the group. To use when the group is deactivated.
            for user in self.user_set.all():
                self.user_set.remove(user)

    def is_manager(self, user):

        if user in self.managers.all():
            return True

        try:
            parent = self.parent
            while parent is not None:
                parent = VPHShareSmartGroup.objects.get(name=parent.name)
                if parent.is_manager(user):
                    return True
                else:
                    parent = parent.parent

        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            return False

        return False

    def get_parents_list_name(self):
        """
        Return the tree list of the parents
        """
        parents_list = []
        try:
            if self.parent:
                parent = self.parent.vphsharesmartgroup
            else:
                parent = self.parent
            while parent is not None:
                if parent.active:
                    parents_list.append(parent.name)
                #follow the tree
                if parent.parent:
                    parent = parent.parent.vphsharesmartgroup
                else:
                    parent = parent.parent
        except Exception, e:
            from raven.contrib.django.raven_compat.models import client
            client.captureException()
            return []
        return parents_list




class Institution(VPHShareSmartGroup):

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

    class Meta:
        verbose_name_plural = "Institutions"
        ordering = ['name']
        permissions = (
            ('can_add_user_to_institution', 'Can add user to Institution'),
        )


class Study(VPHShareSmartGroup):

    start_date = models.DateField(null=True, blank=True, help_text='Study start date')
    finish_date = models.DateField(null=True, blank=True, help_text='Study finish date')

    institution = models.ForeignKey(Institution)

    class Meta:
        verbose_name_plural = "Studies"
        ordering = ['name']
        permissions = (
            ('can_add_user_to_study', 'Can add user to Study'),
        )


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

class InstitutionPortalObject(models.Manager):

    def get(self, *args, **kwargs):
        res = super(InstitutionPortalObject, self).get(*args,**kwargs)
        if res.carusel_img:
            import json
            res.carusel_imgs = json.loads(res.carusel_img)
        return res


class InstitutionPortal(models.Model):

    def get_upload_path(instance, filename):
        return "./institution_portal_folder/%s/%s" % (instance.subdomain,filename)

    #site customization
    institution = models.OneToOneField(Institution, primary_key=True)
    subdomain = models.CharField(verbose_name="Vph-share subdomain", max_length=16, blank=False, help_text='The name of your personal vph-share subdomain - you.vph-share.eu', unique=True, null=False)
    title = models.CharField(verbose_name="Portal title *", max_length=64, blank=False, help_text='Your portal title', null=False)
    welcome = models.CharField(verbose_name="Welcome message *", max_length=200, blank=False, null=False, default="Welcome to our vph-share institutional portal")
    description = models.TextField(verbose_name="Portal description *", null=True)
    background = models.CharField(verbose_name="Background *",max_length=64,  help_text='Background colour')
    header_background = models.CharField(verbose_name="Header background *", max_length=64, help_text='Background colour in the header')
    header_logo = models.FileField(verbose_name="Logo *",  upload_to=get_upload_path, help_text="Logo min size 90x90px" ,null=True)
    carusel_img = models.TextField(null=True, blank = True)

    objects = InstitutionPortalObject()
