# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Institution'
        db.create_table('scs_groups_institution', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('signed_dsa', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('policies_url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('admin_fullname', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('admin_address', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('admin_phone', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('admin_email', self.gf('django.db.models.fields.EmailField')(max_length=64)),
            ('formal_fullname', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('formal_address', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('formal_phone', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('formal_email', self.gf('django.db.models.fields.EmailField')(max_length=64, blank=True)),
            ('breach_fullname', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('breach_address', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('breach_phone', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('breach_email', self.gf('django.db.models.fields.EmailField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('scs_groups', ['Institution'])

        # Adding M2M table for field managers on 'Institution'
        db.create_table('scs_groups_institution_managers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('institution', models.ForeignKey(orm['scs_groups.institution'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('scs_groups_institution_managers', ['institution_id', 'user_id'])

        # Adding model 'Study'
        db.create_table('scs_groups_study', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('finish_date', self.gf('django.db.models.fields.DateField')()),
            ('institution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scs_groups.Institution'])),
        ))
        db.send_create_signal('scs_groups', ['Study'])

        # Adding M2M table for field principals on 'Study'
        db.create_table('scs_groups_study_principals', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('study', models.ForeignKey(orm['scs_groups.study'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('scs_groups_study_principals', ['study_id', 'user_id'])

        # Adding model 'AuditLog'
        db.create_table('scs_groups_auditlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('log', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('scs_groups', ['AuditLog'])

        # Adding model 'SubscriptionRequest'
        db.create_table('scs_groups_subscriptionrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('scs_groups', ['SubscriptionRequest'])


    def backwards(self, orm):
        # Deleting model 'Institution'
        db.delete_table('scs_groups_institution')

        # Removing M2M table for field managers on 'Institution'
        db.delete_table('scs_groups_institution_managers')

        # Deleting model 'Study'
        db.delete_table('scs_groups_study')

        # Removing M2M table for field principals on 'Study'
        db.delete_table('scs_groups_study_principals')

        # Deleting model 'AuditLog'
        db.delete_table('scs_groups_auditlog')

        # Deleting model 'SubscriptionRequest'
        db.delete_table('scs_groups_subscriptionrequest')


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
        'scs_groups.auditlog': {
            'Meta': {'object_name': 'AuditLog'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'scs_groups.institution': {
            'Meta': {'ordering': "['name']", 'object_name': 'Institution', '_ormbases': ['auth.Group']},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'admin_address': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'admin_email': ('django.db.models.fields.EmailField', [], {'max_length': '64'}),
            'admin_fullname': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'admin_phone': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'breach_address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'breach_email': ('django.db.models.fields.EmailField', [], {'max_length': '64', 'blank': 'True'}),
            'breach_fullname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'breach_phone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'formal_address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'formal_email': ('django.db.models.fields.EmailField', [], {'max_length': '64', 'blank': 'True'}),
            'formal_fullname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'formal_phone': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'policies_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'signed_dsa': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'scs_groups.study': {
            'Meta': {'ordering': "['name']", 'object_name': 'Study', '_ormbases': ['auth.Group']},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'finish_date': ('django.db.models.fields.DateField', [], {}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scs_groups.Institution']"}),
            'principals': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'scs_groups.subscriptionrequest': {
            'Meta': {'object_name': 'SubscriptionRequest'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['scs_groups']