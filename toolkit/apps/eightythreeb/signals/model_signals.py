# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from ..models import EightyThreeB, Attachment

import logging
logger = logging.getLogger('django.request')


@receiver(pre_save, sender=EightyThreeB, dispatch_uid='83b.ensure_dates')
def ensure_dates(sender, instance, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    logger.debug('run: 83b.ensure_dates')
    if instance.data.get('date_of_property_transfer', None) is not None:
        if instance.transfer_date in [None, '']:
            instance.transfer_date = instance.get_transfer_date()

        if instance.filing_date in [None, '']:
            instance.filing_date = instance.get_filing_date()


@receiver(post_save, sender=EightyThreeB, dispatch_uid='83b.ensure_83b_user_in_workspace_participants')
def ensure_83b_user_in_workspace_participants(sender, instance, **kwargs):
    logger.debug('run: 83b.ensure_83b_user_in_workspace_participants')
    user = instance.user
    workspace = instance.workspace

    # when we have a new one
    if user not in workspace.participants.all():
        workspace.add_participant(user)


@receiver(post_save, sender=Attachment, dispatch_uid='83b.attachment.ensure_attachment_markers')
def ensure_attachment_markers(sender, instance, **kwargs):
    """
    Delete the copy uploaded Marker when we have no more attachments
    """
    logger.debug('run: 83b.attachment.ensure_attachment_markers')
    eightythreeb = instance.eightythreeb
    # if we have markers
    if 'markers' in eightythreeb.data:
        # if the copy_uploaded is not already present
        if 'copy_uploaded' in eightythreeb.data.get('markers'):
            #
            # We have copy_uploaded present then delete it
            # an save out
            #
            if eightythreeb.attachment_set.all().count() == 0:
                logger.debug('Removing copy_uploaded marker for 83b %s as we have no attachments' % eightythreeb)
                # delete the copy_uploaded marker
                del eightythreeb.data['markers']['copy_uploaded']
                # save
                eightythreeb.save(update_fields=['data'])
        else:
            logger.debug('Added copy_uploaded marker for 83b %s as we have attachments but no marker recorded' % eightythreeb)
            # we need to issue this signal because copy_uploaded is not present
            #
            # If we dont have copy_uploaded in markers then issue this
            #
            eightythreeb.markers.marker('copy_uploaded').issue_signals(request=post_save, instance=instance.eightythreeb, actor=instance.eightythreeb.user)
