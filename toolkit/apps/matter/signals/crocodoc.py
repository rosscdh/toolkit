# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.dispatch import receiver
import dj_crocodoc.signals as crocodoc_signals

#from toolkit.apps.matter.signals import crocodoc_webhook_event_recieved


@receiver(crocodoc_signals.crocodoc_comment_create)
@receiver(crocodoc_signals.crocodoc_comment_update)  # reply to
@receiver(crocodoc_signals.crocodoc_comment_delete)
#@receiver(crocodoc_signals.crocodoc_annotation_highlight)
#@receiver(crocodoc_signals.crocodoc_annotation_strikeout)
@receiver(crocodoc_signals.crocodoc_annotation_textbox)
#@receiver(crocodoc_signals.crocodoc_annotation_drawing)
## @receiver(crocodoc_signals.crocodoc_annotation_point)  # dont record this event because its pretty useless and comes by default when they comment
def crocodoc_webhook_event_recieved(sender, verb, document, target, attachment_name, user_info, crocodoc_event,
                                    content=None, **kwargs):
    """
    signal to handle any of the crocdoc signals
    """
    matter = None

    user_pk, user_full_name = user_info

    try:
        user = User.objects.get(pk=user_pk)

    except User.DoesNotExist:
        pass

    else:
        # continue on we have a user
        #
        # are we looking at something that is a matter
        #
        if target.__class__.__name__ == 'Workspace':
            matter = target
        #
        # are we looking at something that has an item
        #
        if hasattr(target, 'item'):
            matter = target.item.matter

        if matter is not None:
            if crocodoc_event in ['annotation.create', 'comment.create', 'comment.update']:
                # user MUST be in document.source_object.primary_reviewdocument.reviewers
                # otherwise he could not get to this point
                try:
                    reviewdocument = document.source_object.reviewdocument_set.get(crocodoc_uuid=document.uuid)
                except document.source_object.reviewdocument_set.model.DoesNotExist:
                    reviewdocument = None                    

                if reviewdocument:

                    if reviewdocument == document.source_object.primary_reviewdocument:
                        # this reviewdocument is the PRIMARY one, meaning: one that is being reviewed by a matter.participant
                        matter.actions.add_revision_comment(user=user, revision=document.source_object, comment=content,
                                                            reviewdocument=reviewdocument)
                    else:
                        # this reviewdoc is a 3rd party review
                        # otherwise it is externally reviewed -> add "(review copy)" to the displayed event
                        matter.actions.add_review_copy_comment(user=user, revision=document.source_object,
                                                               comment=content, reviewdocument=reviewdocument)

            if crocodoc_event in ['annotation.delete', 'comment.delete']:
                matter.actions.delete_revision_comment(user=user, revision=document.source_object)
