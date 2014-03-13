# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save

from .models import SignDocument


"""
When new SignDocument are created automatically the matter.participants are
added as signdocument.participants and given auth keys
This allows them to enter into conversation with each document
"""


@receiver(post_save, sender=SignDocument, dispatch_uid='sign.ensure_matter_participants_are_in_signdocument_participants')
def ensure_matter_participants_are_in_signdocument_participants(sender, instance, **kwargs):
    """
    When the object is saved we always need to ensure that the matter.participants
    are party to the signs
    """
    matter = instance.document.item.matter
    for u in matter.participants.all():
        if u not in instance.participants.all():
            # add them
            instance.participants.add(u)


def _add_as_authorised(instance, pk_set):
    user = User.objects.filter(pk__in=pk_set).first()
    instance.authorise_user_to_sign(user=user)


def _remove_as_authorised(instance, pk_set):
        user = User.objects.filter(pk__in=pk_set).first()
        instance.deauthorise_user_to_sign(user=user)


"""
Handle when a matter.participant is added to the object
"""


@receiver(m2m_changed, sender=SignDocument.participants.through, dispatch_uid='signdocument.on_participant_add')
def on_participant_add(sender, instance, action, **kwargs):
    """
    when a signer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


@receiver(m2m_changed, sender=SignDocument.participants.through, dispatch_uid='signdocument.on_participant_remove')
def on_participant_remove(sender, instance, action, **kwargs):
    """
    when a signer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


"""
Handle when a signer is added to the object
"""


@receiver(m2m_changed, sender=SignDocument.signatories.through, dispatch_uid='signdocument.on_signer_add')
def on_signer_add(sender, instance, action, **kwargs):
    """
    when a signer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))


@receiver(m2m_changed, sender=SignDocument.signatories.through, dispatch_uid='signdocument.on_signer_remove')
def on_signer_remove(sender, instance, action, **kwargs):
    """
    when a signer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=kwargs.get('pk_set'))
