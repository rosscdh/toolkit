# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save, post_save

from .models import Workspace, Tool

import uuid
import logging
LOGGER = logging.getLogger('django.request')


def _model_slug_exists(model, slug):
    try:
        return model.objects.get(slug=slug)
    except model.DoesNotExist:
        return None


@receiver(pre_save, sender=Workspace, dispatch_uid='workspace.ensure_workspace_slug')
def ensure_workspace_slug(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    workspace = kwargs.get('instance')

    if workspace.slug in [None, '']:

        final_slug = slugify(workspace.name)

        while _model_slug_exists(model=Workspace, slug=final_slug):
            LOGGER.info('Workspace %s exists, trying to create another' % final_slug)

            slug = '%s-%s' % (final_slug, uuid.uuid4().get_hex()[:4])
            slug = slug[:30]
            final_slug = slugify(slug)

        workspace.slug = final_slug


@receiver(post_save, sender=Workspace, dispatch_uid='workspace.ensure_workspace_has_83b_by_default')
def ensure_workspace_has_83b_by_default(sender, **kwargs):
    workspace = kwargs.get('instance')
    created = kwargs.get('created', False)

    # when we have a new one
    if created is True:
        eightythreeb = Tool.objects.get(slug='83b-election-letters')

        if eightythreeb not in workspace.tools.all():
            workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))


@receiver(pre_save, sender=Tool, dispatch_uid='workspace.ensure_tool_slug')
def ensure_tool_slug(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    tool = kwargs.get('instance')
    created = kwargs.get('created', False)

    if tool.slug in [None, '']:

        final_slug = slugify(tool.name)

        while _model_slug_exists(model=Tool, slug=final_slug):
            LOGGER.info('Tool %s exists, trying to create another' % final_slug)

            slug = '%s-%s' % (final_slug, uuid.uuid4().get_hex()[:4])
            slug = slug[:30]
            final_slug = slugify(slug)

        tool.slug = final_slug
