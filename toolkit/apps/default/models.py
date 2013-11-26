# -*- coding: utf-8 -*-
from django.db import models
from uuidfield import UUIDField


class InviteKey(models.Model):
    key = UUIDField(auto=True)
    user = models.ForeignKey('auth.User')