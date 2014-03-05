# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save

from .models import ReviewDocument


"""
When new ReviewDocument are created automatically the matter.participants are
added as reviewdocument.participants and given auth keys
This allows them to enter into conversation with each document
"""


@receiver(post_save, sender=ReviewDocument, dispatch_uid='review.ensure_matter_participants_are_in_reviewdocument_participants')
def ensure_matter_participants_are_in_reviewdocument_participants(sender, instance, **kwargs):
    """
    When the object is saved we always need to ensure that the matter.participants
    are party to the reviews
    """
    matter = instance.document.item.matter
    for u in matter.participants.all():
        if u not in instance.participants.all():
            # add them
            instance.participants.add(u)


def _add_as_authorised(instance, pk_set):
    user = User.objects.filter(pk__in=pk_set).first()
    instance.authorise_user_to_review(user=user)


def _remove_as_authorised(instance, pk_set):
        user = User.objects.filter(pk__in=pk_set).first()
        instance.deauthorise_user_to_review(user=user)


"""
Handle when a matter.participant is added to the object
"""


@receiver(m2m_changed, sender=ReviewDocument.participants.through)
def on_participant_add(sender, instance, action, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


@receiver(m2m_changed, sender=ReviewDocument.participants.through)
def on_participant_remove(sender, instance, action, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


"""
Handle when a reviewer is added to the object
"""


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_add(sender, instance, action, **kwargs):
    """
    when a reviewer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


@receiver(m2m_changed, sender=ReviewDocument.reviewers.through)
def on_reviewer_remove(sender, instance, action, **kwargs):
    """
    when a reviewer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))
