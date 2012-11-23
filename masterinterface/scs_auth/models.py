"""
Extend User model with new attribute in user profile.\n
New fields are:\n
        -postcode.\n
        -country.\n
        -fullname.\n
        -language.\n

"""
__author__ = "Alfredo Saglimbeni (a.saglimbeni@scsitaly.com)"

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class roles(models.Model):

    id=models.AutoField(primary_key=True)
    roleName=models.CharField(max_length=20,unique=True)

class user_role(models.Model):

    username = models.CharField( max_length=30)
    email = models.EmailField( blank=True)
    role = models.ManyToManyField(roles)



class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    postcode = models.CharField(max_length=10, default="")
    country = models.CharField(max_length=20, default="")
    fullname = models.CharField(max_length=30, default="")
    language = models.CharField(max_length=10, default="")
    roles = models.ManyToManyField(roles)

    def to_dict(self):

        user_key =  ['username', 'fullname', 'email', 'language', 'country', 'postcode']

        user_dict={}

        for i in range(0, len(user_key)):
            if getattr(self,user_key[i],None) is not None:
                user_dict[user_key[i]]=getattr(self,user_key[i])
            else:
                user_dict[user_key[i]]=getattr(self.user,user_key[i])

        user_dict['role'] = []
        for value in self.roles.all().values():
            user_dict['role'].append(value['roleName'])
        #user_dict['role'] = []
        #for j in range(0, len(user_roles)):
        #    user_dict['role'].append(user_roles[j]['role'].roleName)

        #### IS NOT A FINAL IMPLEMENTATION ONLY FOR DEVELOPER
        #if user_dict['username']=='mi_testuser':
        #    user_dict['role'] = []
        #else:
        #    user_dict['role'] = ['developer']
            #######
        return user_dict

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)