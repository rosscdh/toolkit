# -*- coding: utf-8 -*-
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed

from toolkit.apps.workspace import _model_slug_exists

from .models import Revision
from toolkit.apps.review.models import ReviewDocument
from toolkit.apps.sign.models import SignDocument

import logging
logger = logging.getLogger('django.request')


@receiver(pre_save, sender=Revision, dispatch_uid='revision.ensure_slug')
def ensure_revision_slug(sender, instance, **kwargs):
    """
    Signal to handle creating the revision slug
    """
    #
    # @BUSINESSRULE Only update the slug if it is a new revision
    #
    if instance.pk is None or instance.slug[0:1] != 'v':  # causes infinite loop if we already have an pk set
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

                while _model_slug_exists(model=Revision, queryset=Revision.objects.exclude(pk=instance.pk).filter(item=instance.item), slug=final_slug):
                    logger.info('Revision.slug %s exists, trying to create another' % final_slug)
                    final_slug = instance.get_revision_label(version=(revision_id + 1))

                instance.slug = final_slug


@receiver(post_save, sender=Revision, dispatch_uid='revision.set_item_is_requested_false')
def set_item_is_requested_false(sender, instance, **kwargs):
    """
    @BUSINESSRULE When uploading a revision to an item
    the event needs to set the item.is_requested = False
    """
    instance.item.is_requested = False
    instance.item.save(update_fields=['is_requested'])


@receiver(pre_save, sender=Revision, dispatch_uid='revision.ensure_one_current_revision')
def ensure_one_current_revision(sender, instance, **kwargs):
    """
    Signal to make sure we only have one current revision for an item.
    """
    if instance.is_current:
        # Make sure we only have one current revision per item
        instance.__class__.objects.filter(item=instance.item).exclude(pk=instance.pk).update(is_current=False)


@receiver(post_save, sender=Revision, dispatch_uid='revision.ensure_revision_reviewdocument_object')
def ensure_revision_reviewdocument_object(sender, instance, **kwargs):
    """
    signal to handle creating the ReviewDocument object for each Revision Object
    which has the matter.participants as the ReviewDocument.participants
    """
    if instance.reviewdocument_set.all().count() == 0:
        with transaction.atomic():
            #
            # Detected that no ReviewDocument is preset
            #
            review_document = ReviewDocument.objects.create(document=instance)
            # now add the revew object to the instance reivewdocument_set
            instance.reviewdocument_set.add(review_document)


@receiver(post_save, sender=Revision, dispatch_uid='revision.ensure_revision_signdocument_object')
def ensure_revision_signdocument_object(sender, instance, **kwargs):
    """
    signal to handle creating the SignDocument object for each Revision Object
    which has the matter.participants as the ReviewDocument.participants
    """
    if instance.signdocument_set.all().count() == 0:
        with transaction.atomic():
            #
            # Detected that no ReviewDocument is preset
            #
            sign_document = SignDocument.objects.create(document=instance)
            # now add the revew object to the instance reivewdocument_set
            instance.signdocument_set.add(sign_document)


@receiver(post_delete, sender=Revision, dispatch_uid='revision.set_previous_revision_is_current_on_delete')
def set_previous_revision_is_current_on_delete(sender, instance, **kwargs):
    """
    @BUSINESSRULE When a lawyer deletes the current revision, then we need to make the previous item in the set
    is_current = True
    """
    previous_revision = instance.__class__.objects.filter(item=instance.item).last()
    if previous_revision:
        previous_revision.is_current = True
        previous_revision.save(update_fields=['is_current'])


@receiver(post_save, sender=Revision, dispatch_uid='revision.set_item_is_requested_false')
def on_upload_set_item_is_requested_false(sender, instance, **kwargs):
    """
    @BUSINESSRULE when a document is uploaded and item.is_requested = True
    and its uploaded by the item.responsible_party then mark it as is_requested = False
    """
    if instance.item.is_requested is True:
        if instance.uploaded_by == instance.item.responsible_party:
            item = instance.item
            item.is_requested = False
            item.save(update_fields=['is_requested'])
            # @TODO issue activity here?


"""
Reviewers
reviewdocuments have 1 object per reviewer this is to ensure a unique auth url for each reviewer
and to ensure there is a sandbox view where only the matter participants and the invited reviewer
can talk
"""


@receiver(m2m_changed, sender=Revision.reviewers.through, dispatch_uid='revision.on_reviewer_add')
def on_reviewer_add(sender, instance, action, model, pk_set, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add'] and pk_set:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)  # get the user being invited

        #
        # Get the base review documnet; created to alow the participants to access
        # and discuss a documnet
        #
        reviewdocument = instance.reviewdocument_set.all().first()

        #
        # 1 ReviewDocument per reviewer
        # in this case we should immediately delete the review document
        #
        reviewdocument.pk = None  # set to null this is adjango stategy to copy the model
        reviewdocument.slug = None  # set to non so it gets regenerated
        reviewdocument.save()  # save it so we get a new pk so we can add reviewrs
        reviewdocument.reviewers.add(user)  # add the reviewer
        reviewdocument.recompile_auth_keys()  # update teh auth keys to match the new slug


@receiver(m2m_changed, sender=Revision.reviewers.through, dispatch_uid='revision.on_reviewer_remove')
def on_reviewer_remove(sender, instance, action, model, pk_set, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    """
    if action in ['pre_remove'] and pk_set:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)

        reviewdocuments = instance.reviewdocument_set.filter(reviewers__in=[user])

        #
        # 1 ReviewDocument per reviewer
        # in this case we should immediately delete the review document
        #
        for reviewdocument in reviewdocuments:
            # delete the reviewdoc
            reviewdocument.delete()


"""
Signers
Unlike reviewrs, signdocuments have only 1 object per set of signature invitees
"""


@receiver(m2m_changed, sender=Revision.signers.through, dispatch_uid='revision.on_signatory_add')
def on_signatory_add(sender, instance, action, model, pk_set, **kwargs):
    """
    when a signatory is added from the m2m then authorise them
    for access
    """
    if action in ['post_add'] and pk_set:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)

        #
        # Get the base review documnet; created to alow the participants to access
        # and discuss a documnet
        #
        signdocument = instance.signdocument_set.all().first()

        #
        # 1 SignDocument for the entire set of invitees
        #
        signdocument.signers.add(user)  # allow the user to have access


@receiver(m2m_changed, sender=Revision.signers.through, dispatch_uid='revision.on_signatory_remove')
def on_signatory_remove(sender, instance, action, model, pk_set, **kwargs):
    """
    when a signatory is removed from the m2m then deauthorise them
    """
    if action in ['pre_remove'] and pk_set:
        user_pk = next(iter(pk_set))  # get the first item in the set should only ever be 1 anyway
        user = model.objects.get(pk=user_pk)

        signdocuments = instance.signdocument_set.filter(signers__in=[user])

        #
        # 1 SignDocument per signatory
        # in this case we should immediately delete the review document
        #
        for signdocument in signdocuments:
            # delete the reviewdoc
            signdocument.signers.remove(user)
