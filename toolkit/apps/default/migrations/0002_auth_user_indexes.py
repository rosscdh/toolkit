# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        db.create_index(u'auth_user', ['email'])
        db.create_index(u'auth_user', ['username'])

    def backwards(self, orm):
        db.delete_index(u'auth_user', ['email'])
        db.delete_index(u'auth_user', ['username'])


    symmetrical = False

