# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TavernaExecution.creation_datetime'
        db.add_column('scs_workspace_tavernaexecution', 'creation_datetime',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.executionstatus'
        db.add_column('scs_workspace_tavernaexecution', 'executionstatus',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.error'
        db.add_column('scs_workspace_tavernaexecution', 'error',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.error_msg'
        db.add_column('scs_workspace_tavernaexecution', 'error_msg',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.endpoint'
        db.add_column('scs_workspace_tavernaexecution', 'endpoint',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=600, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.asConfigId'
        db.add_column('scs_workspace_tavernaexecution', 'asConfigId',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=80, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.expiry'
        db.add_column('scs_workspace_tavernaexecution', 'expiry',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=80, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.startTime'
        db.add_column('scs_workspace_tavernaexecution', 'startTime',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=80, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.Finished'
        db.add_column('scs_workspace_tavernaexecution', 'Finished',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.exitcode'
        db.add_column('scs_workspace_tavernaexecution', 'exitcode',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.stdout'
        db.add_column('scs_workspace_tavernaexecution', 'stdout',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.stderr'
        db.add_column('scs_workspace_tavernaexecution', 'stderr',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'TavernaExecution.outputfolder'
        db.add_column('scs_workspace_tavernaexecution', 'outputfolder',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=600, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TavernaExecution.creation_datetime'
        db.delete_column('scs_workspace_tavernaexecution', 'creation_datetime')

        # Deleting field 'TavernaExecution.executionstatus'
        db.delete_column('scs_workspace_tavernaexecution', 'executionstatus')

        # Deleting field 'TavernaExecution.error'
        db.delete_column('scs_workspace_tavernaexecution', 'error')

        # Deleting field 'TavernaExecution.error_msg'
        db.delete_column('scs_workspace_tavernaexecution', 'error_msg')

        # Deleting field 'TavernaExecution.endpoint'
        db.delete_column('scs_workspace_tavernaexecution', 'endpoint')

        # Deleting field 'TavernaExecution.asConfigId'
        db.delete_column('scs_workspace_tavernaexecution', 'asConfigId')

        # Deleting field 'TavernaExecution.expiry'
        db.delete_column('scs_workspace_tavernaexecution', 'expiry')

        # Deleting field 'TavernaExecution.startTime'
        db.delete_column('scs_workspace_tavernaexecution', 'startTime')

        # Deleting field 'TavernaExecution.Finished'
        db.delete_column('scs_workspace_tavernaexecution', 'Finished')

        # Deleting field 'TavernaExecution.exitcode'
        db.delete_column('scs_workspace_tavernaexecution', 'exitcode')

        # Deleting field 'TavernaExecution.stdout'
        db.delete_column('scs_workspace_tavernaexecution', 'stdout')

        # Deleting field 'TavernaExecution.stderr'
        db.delete_column('scs_workspace_tavernaexecution', 'stderr')

        # Deleting field 'TavernaExecution.outputfolder'
        db.delete_column('scs_workspace_tavernaexecution', 'outputfolder')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'scs_workspace.tavernaexecution': {
            'Finished': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'Meta': {'object_name': 'TavernaExecution'},
            'asConfigId': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'as_config_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'baclava': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '600', 'blank': 'True'}),
            'error': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'executionstatus': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exitcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'expiry': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'outputfolder': ('django.db.models.fields.CharField', [], {'max_length': '600', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'startTime': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Initialized'", 'max_length': '80'}),
            'stderr': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'stdout': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            't2flow': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'taverna_atomic_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'taverna_id': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'workflowId': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        }
    }

    complete_apps = ['scs_workspace']