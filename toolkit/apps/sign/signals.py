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
    model_data = hellosign_request.data.get('signature_request', {})  # it may not be set yet? # this is weird if it is the case

    if not model_data:  # if its an empty dict
        logger.error('hellosign_request.data is empty this is a bit weird: %s' % hellosign_request.pk)

    # update the model with the data we got from HS
    model_data.update(data['signature_request'])
    # udpate the main model data
    hellosign_request.data = model_data

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
def reset_recalculate_signing_percentage_complete_post_save(sender, instance, created, update_fields, **kwargs):
    item = instance.document.item
    item.recalculate_signing_percentage_complete()


@receiver(post_delete, sender=SignDocument, dispatch_uid='sign.pre_delete.reset_recalculate_signing_percentage_complete')
def reset_recalculate_signing_percentage_complete_post_delete(sender, instance, **kwargs):
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
def _get_user_from_event_data(event_data):
    signature_request = event_data.get('signature_request', {})
    event_data = event_data.get('event', {})
    event_metadata = event_data.get('event_metadata', {})
    user = None

    # Send event
    related_signature_id = event_metadata.get('related_signature_id', None)
    related_email_address = None

    try:
        signer = [signer for signer in signature_request.get('signatures', []) if related_signature_id == signer.get('signature_id')][0]
        related_email_address = signer.get('signer_email_address')

    except IndexError:
        logging.error('Could not related signer in HelloSign event.signature_request.signatures')

    if related_email_address:
        user = User.objects.get(email=related_email_address)

    return user


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

        #
        # ALL HAVE SIGNED
        #
        if event_type == 'signature_request_all_signed':
            logging.info('Recieved signature_request_all_signed from HelloSign, downloading file for attachment as final')
            # update request
            _update_signature_request(hellosign_request=hellosign_request, data=data)

            # Send event
            hellosign_request.source_object.document.item.matter.actions.all_users_have_signed(sign_object=hellosign_request.source_object)

            #
            # Download the file and update the item.latest_revision
            #
            run_task(_download_signing_complete_document, hellosign_request=hellosign_request, data=data)

        #
        # USER SIGNED
        #
        if event_type == 'signature_request_signed':
            logging.info('Recieved signature_request_signed from HelloSign, sending event notice')
            # update the signature_request data with our newly provided data
            _update_signature_request(hellosign_request=hellosign_request, data=data)

            # Send event
            user = _get_user_from_event_data(event_data=data)
            if user:
                hellosign_request.source_object.document.item.matter.actions.user_signed(user=user, sign_object=hellosign_request.source_object)

        if event_type == 'signature_request_viewed':
            #
            # NOT HANDLED HERE rather in toolkit.api.views.sign
            # REASON: because the lawyer can view signature requests at their
            # distinct urls and may not actually be the invited signer
            #

            # user = _get_user_from_event_data(event_data=data)
            # if user:
            #     revision = hellosign_request.source_object.document
            #     item = revision.item
            #     matter = item.matter
            #     matter.actions.user_viewed_signature_request(item=revision.item,
            #                                                  user=user,
            #                                                  revision=revision)
            pass
