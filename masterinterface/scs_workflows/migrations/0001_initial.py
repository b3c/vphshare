# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'scsWorkflow'
        db.create_table('scs_workflows_scsworkflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('t2flow', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('xml', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('metadataId', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
        ))
        db.send_create_signal('scs_workflows', ['scsWorkflow'])


    def backwards(self, orm):
        # Deleting model 'scsWorkflow'
        db.delete_table('scs_workflows_scsworkflow')


    models = {
        'scs_workflows.scsworkflow': {
            'Meta': {'object_name': 'scsWorkflow'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadataId': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            't2flow': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'xml': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['scs_workflows']