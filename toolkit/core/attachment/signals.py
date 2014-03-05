# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_save

from toolkit.apps.workspace.signals import _model_slug_exists

from .models import Revision


import uuid
import logging
logger = logging.getLogger('django.request')


@receiver(pre_save, sender=Revision, dispatch_uid='revision.ensure_slug')
def ensure_revision_slug(sender, instance, **kwargs):
    """
    signal to handle creating the revision slug
    """
    #
    # Dont perform this action if we are manually updating the slug
    #

    #Update fields is none is the revision is newly created
    if kwargs['update_fields'] is not None and 'slug' not in kwargs['update_fields']:

        if instance.slug in [None, '']:
            revision_id = int(instance.get_revision_id())
            final_slug = instance.get_revision_label(version=revision_id)

            while _model_slug_exists(model=Revision, slug=final_slug):
                logger.info('Revision.slug %s exists, trying to create another' % final_slug)
                final_slug = instance.get_revision_label(version=(revision_id + 1))

            instance.slug = final_slug
