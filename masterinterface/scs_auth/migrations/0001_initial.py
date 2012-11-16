# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'roles'
        db.create_table('scs_auth_roles', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('roleName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal('scs_auth', ['roles'])

        # Adding model 'user_role'
        db.create_table('scs_auth_user_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('scs_auth', ['user_role'])

        # Adding M2M table for field role on 'user_role'
        db.create_table('scs_auth_user_role_role', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user_role', models.ForeignKey(orm['scs_auth.user_role'], null=False)),
            ('roles', models.ForeignKey(orm['scs_auth.roles'], null=False))
        ))
        db.create_unique('scs_auth_user_role_role', ['user_role_id', 'roles_id'])

        # Adding model 'UserProfile'
        db.create_table('scs_auth_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('country', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('fullname', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
            ('language', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
        ))
        db.send_create_signal('scs_auth', ['UserProfile'])

        # Adding M2M table for field roles on 'UserProfile'
        db.create_table('scs_auth_userprofile_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['scs_auth.userprofile'], null=False)),
            ('roles', models.ForeignKey(orm['scs_auth.roles'], null=False))
        ))
        db.create_unique('scs_auth_userprofile_roles', ['userprofile_id', 'roles_id'])


    def backwards(self, orm):
        # Deleting model 'roles'
        db.delete_table('scs_auth_roles')

        # Deleting model 'user_role'
        db.delete_table('scs_auth_user_role')

        # Removing M2M table for field role on 'user_role'
        db.delete_table('scs_auth_user_role_role')

        # Deleting model 'UserProfile'
        db.delete_table('scs_auth_userprofile')

        # Removing M2M table for field roles on 'UserProfile'
        db.delete_table('scs_auth_userprofile_roles')


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
        'scs_auth.roles': {
            'Meta': {'object_name': 'roles'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roleName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'scs_auth.user_role': {
            'Meta': {'object_name': 'user_role'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['scs_auth.roles']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'scs_auth.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'fullname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'postcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['scs_auth.roles']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['scs_auth']