# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from toolkit.apps.workspace.signals import _model_slug_exists

from .models import Revision
from toolkit.apps.review.models import ReviewDocument

import uuid
import logging
logger = logging.getLogger('django.request')


@receiver(pre_save, sender=Revision, dispatch_uid='revision.ensure_slug')
def ensure_revision_slug(sender, instance, **kwargs):
    """
    Signal to handle creating the revision slug
    """
    #
    # Dont perform this action if we are manually updating the slug
    #
    # only do this if we have no specific fields to update
    # but not if we do have updated_fields and the slug is being set
    if kwargs['update_fields'] is None or 'slug' not in kwargs['update_fields']:
        #
        # if the slug somehow gets set as somethign weird like a normal slug
        # then take it back and make it a vXXX number
        #
        if instance.slug in [None, ''] or instance.slug[0:1] != 'v':
            revision_id = int(instance.get_revision_id())
            final_slug = instance.get_revision_label(version=revision_id)

            while _model_slug_exists(model=Revision, queryset=Revision.objects.filter(item=instance.item), slug=final_slug):
                logger.info('Revision.slug %s exists, trying to create another' % final_slug)
                final_slug = instance.get_revision_label(version=(revision_id + 1))

            instance.slug = final_slug


@receiver(post_save, sender=Revision, dispatch_uid='revision.ensure_revision_initial_reviewdocument')
def ensure_revision_initial_reviewdocument(sender, instance, **kwargs):
    """
    signal to handle creating the DocumentReview object for the initial Revision
    """
    if instance.reviewdocument_set.all().count() == 0:
        #
        # Detected that no ReviewDocument is preset
        #
        instance.reviewdocument_set.add(ReviewDocument.objects.create(document=instance))
