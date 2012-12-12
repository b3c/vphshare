"""
    scs_search: models.py Module
"""

from django.db import models


class Query( models.Model ):
    """
    """

    id = models.AutoField( primary_key = True )
    date = models.DateField( auto_now = True )
    name = models.CharField( max_length = 100, default = "" )
    user_id = models.IntegerField( null=False )


class Terms( models.Model ):
    """
    """

    id = models.AutoField( primary_key = True )
    concept_name = models.CharField( max_length = 100, null = False )
    concept_uri = models.CharField( max_length = 100, null = False )


class Groups( models.Model ):
    """
    """

    group_id = models.IntegerField( null=False )
    query = models.ManyToManyField( Query )
    terms = models.ManyToManyField( Terms )



