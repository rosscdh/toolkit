# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Workspace'
        db.create_table(u'workspace_workspace', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('lawyer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lawyer_workspace', null=True, to=orm['auth.User'])),
            ('data', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, db_index=True, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'workspace', ['Workspace'])

        # Adding M2M table for field participants on 'Workspace'
        m2m_table_name = db.shorten_name(u'workspace_workspace_participants')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workspace', models.ForeignKey(orm[u'workspace.workspace'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['workspace_id', 'user_id'])

        # Adding M2M table for field tools on 'Workspace'
        m2m_table_name = db.shorten_name(u'workspace_workspace_tools')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workspace', models.ForeignKey(orm[u'workspace.workspace'], null=False)),
            ('tool', models.ForeignKey(orm[u'workspace.tool'], null=False))
        ))
        db.create_unique(m2m_table_name, ['workspace_id', 'tool_id'])

        # Adding model 'InviteKey'
        db.create_table(u'workspace_invitekey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('uuidfield.fields.UUIDField')(db_index=True, unique=True, max_length=32, blank=True)),
            ('invited_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitations', to=orm['auth.User'])),
            ('inviting_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invitiations_made', to=orm['auth.User'])),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workspace.Tool'], blank=True)),
            ('tool_object_id', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('next', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
            ('has_been_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'workspace', ['InviteKey'])

        # Adding model 'Tool'
        db.create_table(u'workspace_tool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
        ))
        db.send_create_signal(u'workspace', ['Tool'])


    def backwards(self, orm):
        # Deleting model 'Workspace'
        db.delete_table(u'workspace_workspace')

        # Removing M2M table for field participants on 'Workspace'
        db.delete_table(db.shorten_name(u'workspace_workspace_participants'))

        # Removing M2M table for field tools on 'Workspace'
        db.delete_table(db.shorten_name(u'workspace_workspace_tools'))

        # Deleting model 'InviteKey'
        db.delete_table(u'workspace_invitekey')

        # Deleting model 'Tool'
        db.delete_table(u'workspace_tool')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'workspace.invitekey': {
            'Meta': {'object_name': 'InviteKey'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'has_been_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': u"orm['auth.User']"}),
            'inviting_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitiations_made'", 'to': u"orm['auth.User']"}),
            'key': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'next': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['workspace.Tool']", 'blank': 'True'}),
            'tool_object_id': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        u'workspace.tool': {
            'Meta': {'ordering': "['name']", 'object_name': 'Tool'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'workspace.workspace': {
            'Meta': {'ordering': "['name', '-pk']", 'object_name': 'Workspace'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'lawyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lawyer_workspace'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'tools': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['workspace.Tool']", 'symmetrical': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['workspace']