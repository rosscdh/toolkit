# -*- coding: utf-8 -*-
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, m2m_changed

from toolkit.apps.workspace.signals import _model_slug_exists

from toolkit.apps.review import (ASSOCIATION_STRATEGIES,
                                 REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY,)

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


@receiver(post_save, sender=Revision, dispatch_uid='revision.ensure_revision_reviewdocument_object')
def ensure_revision_reviewdocument_object(sender, instance, **kwargs):
    """
    signal to handle creating the DocumentReview object for each Revision Object
    which has the matter.participants as the ReviewDocument.participants
    """
    if instance.reviewdocument_set.all().count() == 0:
        with transaction.atomic():
            #
            # Detected that no ReviewDocument is preset
            #
            review = ReviewDocument.objects.create(document=instance)
            # set the review participants to be the same as the matter.participants
            review.participants = instance.item.matter.participants.all()
            # now add the revew object to the instance reivewdocument_set
            instance.reviewdocument_set.add(review)


@receiver(m2m_changed, sender=Revision.reviewers.through, dispatch_uid='revision.on_reviewer_add')
def on_reviewer_add(sender, instance, action, model, pk_set, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)  # get the user being invited

        #
        # Get the base review documnet; created to alow the participants to access
        # and discuss a documnet
        #
        reviewdocument = instance.reviewdocument_set.all().first()

        if REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY == ASSOCIATION_STRATEGIES.single:
            #
            # 1 ReviewDocument per reviewer
            # in this case we should immediately delete the review document
            #
            reviewdocument.pk = None  # set to null this is adjango stategy to copy the model
            reviewdocument.slug = None  # set to non so it gets regenerated
            reviewdocument.save()  # save it so we get a new pk so we can add reviewrs
            reviewdocument.reviewers.add(user)  # add the reviewer
            reviewdocument.recompile_auth_keys()  # update teh auth keys to match the new slug

        if REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY == ASSOCIATION_STRATEGIES.multi:
            #
            # Multiple reviewers per reviewer document
            # just add the user to reviewres if they dont exist

            #
            reviewdocument.reviewers.add(user) if user not in reviewdocument.reviewers.all() else None


@receiver(m2m_changed, sender=Revision.reviewers.through, dispatch_uid='revision.on_reviewer_remove')
def on_reviewer_remove(sender, instance, action, model, pk_set, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    """
    if action in ['pre_remove']:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)

        reviewdocuments = ReviewDocument.objects.filter(document=instance,
                                                        reviewers__in=[user])

        if REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY == ASSOCIATION_STRATEGIES.single:
            #
            # 1 ReviewDocument per reviewer
            # in this case we should immediately delete the review document
            #
            for reviewdocument in reviewdocuments:
                # delete the reviewdoc
                reviewdocument.delete()

        elif REVIEWER_DOCUMENT_ASSOCIATION_STRATEGY == ASSOCIATION_STRATEGIES.multi:
            #
            # Multiple reviewers per reviewer document only remove them as reviewers
            # but leave the document object alone!
            #
            for reviewdocument in reviewdocuments:
                reviewdocument.reviewers.remove(user) if user in reviewdocument.reviewers.all() else None


