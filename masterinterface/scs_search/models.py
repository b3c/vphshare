"""
    scs_search: models.py Module
"""

from django.db import models
from django.contrib.auth.models import User


class Query( models.Model ):
    """
    """

    id = models.AutoField( primary_key = True )
    date = models.DateTimeField( auto_now = True )
    name = models.CharField( max_length = 100, default = "" )
    user = models.ManyToManyField( User )
    query = models.TextField()
    saved = models.BooleanField(default = False)


    def __unicode__(self):
        return self.name


