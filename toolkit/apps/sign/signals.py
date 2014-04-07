# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save

from hello_sign.signals import hellosign_webhook_event_recieved

from .models import SignDocument


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
When new SignDocument are created automatically the matter.participants are
added as signdocument.participants and given auth keys
This allows them to enter into conversation with each document
"""


@receiver(post_save, sender=SignDocument, dispatch_uid='sign.ensure_matter_participants_are_in_signdocument_participants')
def ensure_matter_participants_are_in_signdocument_participants(sender, instance, **kwargs):
    """
    When the object is saved we always need to ensure that the matter.participants
    are party to the reviews
    """
    matter = instance.document.item.matter
    # used to check for deletions
    authorised_user_pks = [u.pk for u in instance.signers.all()]  # current signers

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
Handle when a signer is added to the object
"""


@receiver(m2m_changed, sender=SignDocument.signers.through, dispatch_uid='signdocument.on_signer_add')
def on_signer_add(sender, instance, action, pk_set, **kwargs):
    """
    when a signer is added from the m2m then authorise them
    for access
    """
    if action in ['post_add']:
        _add_as_authorised(instance=instance, pk_set=pk_set)


@receiver(m2m_changed, sender=SignDocument.signers.through, dispatch_uid='signdocument.on_signer_remove')
def on_signer_remove(sender, instance, action, pk_set, **kwargs):
    """
    when a signer is removed from the m2m then deauthorise them
    """
    if action in ['post_remove']:
        _remove_as_authorised(instance=instance, pk_set=pk_set)


"""
HelloSign webhook
"""

@receiver(hellosign_webhook_event_recieved)
def on_hellosign_webhook_event_recieved(sender, hellosign_log,
                                        signature_request_id,
                                        hellosign_request,
                                        event_type,
                                        data,
                                        **kwargs):
    #
    # Head the signal
    #
    signature_doc = hellosign_request.source_object

    if signature_doc.__class__.__name__ in ['SignDocument']:
        logging.info('Recieved event: %s for request: %s' % (event_type, hellosign_request,))

        if hellosign_log.event_type == 'signature_request_all_signed':
            #import pdb;pdb.set_trace()
            logging.info('Recieved signature_request_all_signed from HelloSign')

        elif hellosign_log.event_type == 'signature_request_signed':
            #import pdb;pdb.set_trace()
            logging.info('Recieved signature_request_signed from HelloSign')