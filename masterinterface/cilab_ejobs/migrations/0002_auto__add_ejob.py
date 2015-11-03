# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EJob'
        db.create_table('cilab_ejobs_ejob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modification_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('completion_timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('state', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('message', self.gf('django.db.models.fields.CharField')(default='', max_length=1024)),
            ('input_data', self.gf('django.db.models.fields.TextField')(default='', max_length=4096)),
            ('output_data', self.gf('django.db.models.fields.TextField')(default='', max_length=4096)),
            ('owner_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('worker_id', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('cilab_ejobs', ['EJob'])


    def backwards(self, orm):
        # Deleting model 'EJob'
        db.delete_table('cilab_ejobs_ejob')


    models = {
        'cilab_ejobs.ejob': {
            'Meta': {'object_name': 'EJob'},
            'completion_timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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