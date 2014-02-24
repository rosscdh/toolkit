from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    lawyer = models.ForeignKey('auth.User')


from .signals import (ensure_client_slug,)