# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save, post_save, pre_delete

from .models import Workspace

import uuid
import logging
LOGGER = logging.getLogger('django.request')


def _workspace_slug_exists(slug):
    try:
        return Workspace.objects.get(slug=slug)
    except Workspace.DoesNotExist:
        return None


@receiver(pre_save, sender=Workspace, dispatch_uid='workspace.ensure_workspace_slug')
def ensure_workspace_slug(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    workspace = kwargs.get('instance')
    created = kwargs.get('created', False)

    if workspace.slug in [None, '']:

        final_slug = slugify(workspace.name)

        while _workspace_slug_exists(slug=final_slug):
            LOGGER.info('Workspace %s exists, trying to create another' % final_slug)

            slug = '%s-%s' % (final_slug, uuid.uuid4().get_hex()[:4])
            slug = slug[:30]
            final_slug = slugify(slug)

        workspace.slug = final_slug