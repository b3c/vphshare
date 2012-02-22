from django.db import models

# Create your models here.

class UserManager(models.Manager):
    def create_user(self, username, email):
        return self.model._default_manager.create(username=username)


class User(models.Model):
    username = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(null=False,default=True)

    objects = UserManager()

    def is_authenticated(self):
        return True