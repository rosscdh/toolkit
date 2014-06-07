# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WorkspaceParticipants.is_matter_owner'
        db.add_column('workspace_workspace_participants', 'is_matter_owner',
                      self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True),
                      keep_default=False)

        # Adding field 'WorkspaceParticipants.data'
        db.add_column('workspace_workspace_participants', 'data',
                      self.gf('jsonfield.fields.JSONField')(default={}),
                      keep_default=False)

        # Adding field 'WorkspaceParticipants.role'
        db.add_column('workspace_workspace_participants', 'role',
                      self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WorkspaceParticipants.is_matter_owner'
        db.delete_column('workspace_workspace_participants', 'is_matter_owner')

        # Deleting field 'WorkspaceParticipants.data'
        db.delete_column('workspace_workspace_participants', 'data')

        # Deleting field 'WorkspaceParticipants.role'
        db.delete_column('workspace_workspace_participants', 'role')


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
        u'client.client': {
            'Meta': {'object_name': 'Client'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lawyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clients'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'})
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
            'inviting_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invitiations_made'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'key': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'matter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['workspace.Workspace']", 'null': 'True', 'blank': 'True'}),
            'next': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['workspace.Tool']", 'null': 'True', 'blank': 'True'}),
            'tool_object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['client.Client']", 'null': 'True', 'blank': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lawyer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lawyer_workspace'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'matter_code': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'through': u"orm['workspace.WorkspaceParticipants']", 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'tools': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['workspace.Tool']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'workspace.workspaceparticipants': {
            'Meta': {'object_name': 'WorkspaceParticipants', 'db_table': "'workspace_workspace_participants'"},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_matter_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'workspace': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['workspace.Workspace']", 'db_column': "'workspace_id'"}),
            'role': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'db_column': "'user_id'"})
        }
    }

    complete_apps = ['workspace']