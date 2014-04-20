# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save, post_delete

from .models import ReviewDocument


def _add_as_authorised(instance, pk_set):
    if pk_set:
        user = User.objects.filter(pk__in=pk_set).first()
        instance.authorise_user_access(user=user)
        instance.save(update_fields=['data'])


def _remove_as_authorised(instance, pk_set):
    if pk_set:
        user = User.objects.filter(pk__in=pk_set).first()
        instance.deauthorise_user_access(user=user)
        instance.save(update_fields=['data'])

"""
When new ReviewDocument are created automatically the matter.participants are
added as reviewdocument.auth and given auth keys
This allows them to enter into conversation with each document and its invited
reviewer
"""

@receiver(post_save, sender=ReviewDocument, dispatch_uid='review.post_save.reset_item_review_percentage_complete_on_complete')
def reset_item_review_percentage_complete_on_complete(sender, instance, created, update_fields, **kwargs):
    item = instance.document.item
    item.recalculate_review_percentage_complete()

    if item.review_percentage_complete == 100.0:
        # send matter.action signal
        item.matter.actions.all_revision_reviews_complete(item=item, revision=instance.document)


@receiver(post_delete, sender=ReviewDocument, dispatch_uid='review.pre_delete.reset_item_review_percentage_complete')
def reset_item_review_percentage_complete_on_delete(sender, instance, **kwargs):
    item = instance.document.item
    item.recalculate_review_percentage_complete()


@receiver(post_save, sender=ReviewDocument, dispatch_uid='review.ensure_matter_participants_are_in_reviewdocument_participants')
def ensure_matter_participants_are_in_reviewdocument_participants(sender, instance, **kwargs):
    """
    When the object is saved we always need to ensure that the matter.participants
    are party to the reviews
    """
    matter = instance.document.item.matter
    # used to check for deletions
    authorised_user_pks = [u.pk for u in instance.reviewers.all()]  # current reviewers

    for u in matter.participants.all():
        authorised_user_pks.append(u.pk) # these guys are in by default

        if instance.get_user_auth(user=u) is None:
            # add them
            _add_as_authorised(instance=instance, pk_set=[u.pk])
    #
    # Cleanup after onesself
    # get current set of authorised_user_pks
    # adn ensure there are no excessive (older, users that were in the matter but are now not) ones in there
    #
    for pk in instance.auth.keys():
        if int(pk) not in authorised_user_pks:
            _remove_as_authorised(instance=instance, pk_set=[pk])


"""
Handle when a reviewer is added to the object
reviewers are the 3rd party entity NOT participants
"""


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through, dispatch_uid='reviewdocument.on_reviewer_add')
def on_reviewer_add(sender, instance, action, pk_set, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    only reviewers get action events
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=pk_set)


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through, dispatch_uid='reviewdocument.on_reviewer_remove')
def on_reviewer_remove(sender, instance, action, pk_set, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    only reviewers get action events
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=pk_set)
