# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save, post_save, pre_delete

from .models import Workspace


@receiver(pre_save, sender=Workspace, dispatch_uid='workspace.ensure_workspace_slug')
def ensure_workspace_slug(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    workspace = kwargs.get('instance')
    created = kwargs.get('created', False)

    if created is True:
        if workspace.slug in [None, '']:
            workspace.slug = slugify(workspace.name)