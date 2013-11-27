# -*- coding: utf-8 -*-
from django.db import models
from jsonfield import JSONField


class EightyThreeB(models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')
    data = JSONField(default={})