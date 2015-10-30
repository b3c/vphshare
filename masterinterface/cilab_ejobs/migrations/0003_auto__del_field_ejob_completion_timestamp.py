# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'EJob.completion_timestamp'
        db.delete_column('cilab_ejobs_ejob', 'completion_timestamp')


    def backwards(self, orm):
        # Adding field 'EJob.completion_timestamp'
        db.add_column('cilab_ejobs_ejob', 'completion_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


    models = {
        'cilab_ejobs.ejob': {
            'Meta': {'object_name': 'EJob'},
            'creation_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_data': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '4096'}),
            'message': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024'}),
            'modification_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'output_data': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '4096'}),
            'owner_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'worker_id': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['cilab_ejobs']