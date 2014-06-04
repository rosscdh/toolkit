# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save, post_delete

from hello_sign.signals import hellosign_webhook_event_recieved

from toolkit.tasks import run_task

from .models import SignDocument
from .tasks import _download_signing_complete_document

import logging
logger = logging.getLogger('django.request')


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


def _update_signature_request(hellosign_request, data):
    hellosign_request.data['signature_request'].update(data['signature_request'])
    hellosign_request.save(update_fields=['data']) # save it # possible race condition here
    # Recalculate the percentage complete
    hellosign_request.source_object.document.item.recalculate_signing_percentage_complete()

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


@receiver(post_save, sender=SignDocument, dispatch_uid='sign.post_save.reset_recalculate_signing_percentage_complete')
def reset_recalculate_signing_percentage_complete(sender, instance, created, update_fields, **kwargs):
    item = instance.document.item
    item.recalculate_signing_percentage_complete()


@receiver(post_delete, sender=SignDocument, dispatch_uid='sign.pre_delete.reset_recalculate_signing_percentage_complete')
def reset_recalculate_signing_percentage_complete(sender, instance, **kwargs):
    item = instance.document.item
    item.recalculate_signing_percentage_complete()


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

        if event_type == 'signature_request_all_signed':
            logging.info('Recieved signature_request_all_signed from HelloSign, downloading file for attachment as final')
            _update_signature_request(hellosign_request=hellosign_request, data=data)
            #
            # Download the file and update the item.latest_revision
            #
            run_task(_download_signing_complete_document, hellosign_request=hellosign_request, data=data)

        if event_type == 'signature_request_signed':
            logging.info('Recieved signature_request_signed from HelloSign, sending event notice')
            # update the signature_request data with our newly provided data
            _update_signature_request(hellosign_request=hellosign_request, data=data)

        if event_type == 'signature_request_viewed':
            # *sigh* HS dont really provide any info on.. WHO viewed...
            pass
