# -*- coding: utf-8 -*-
"""
Item signals to handle various events that take place on save
"""
import logging
logger = logging.getLogger('django.request')


def on_item_save_category(sender, instance, **kwargs):
    """
    Update and modify matter categories when item is changes
    """
    matter = instance.matter
    previous_instance = None
    prev_cat = None
    new_cat = instance.category

    try:
        # get the current
        previous_instance = sender.objects.get(pk=instance.pk)
        prev_cat = previous_instance.category

    except sender.DoesNotExist:
        #
        # Do nothing as the previous object does not exist
        #
        pass

    # compare
    if prev_cat != new_cat:
        #
        # We want to remove the previous cat from the matter
        #
        if previous_instance is not None:
            matter.remove_category(prev_cat, instance=previous_instance)

    # add the new cat to the matter
    matter.add_category(new_cat)
    # save the matter
    matter.save(update_fields=['data'])  # save the updated data where categories are stored

    logger.debug('Recieved item.pre_save:category event: %s' % sender)


def on_item_save_closing_group(sender, instance, **kwargs):
    """
    Update and modify matter closing_group when item is changes
    """
    matter = instance.matter
    prev_cg = None
    new_cg = instance.closing_group

    try:
        # get the current
        previous_instance = sender.objects.get(pk=instance.pk)
        prev_cg = previous_instance.closing_group

    except sender.DoesNotExist:
        #
        # Do nothing as the previous object does not exist
        #
        pass

    if prev_cg != new_cg:
        #
        # We want to remove the previous cat from the matter
        #
        matter.remove_closing_group(prev_cg, instance=instance)

    # add the new cat to the matter
    matter.add_closing_group(new_cg)
    # save the matter
    matter.save(update_fields=['data'])  # save the updated data where categories are stored

    logger.debug('Recieved item.pre_save:closing_group event: %s' % sender)


def on_item_save_changed_status(sender, instance, **kwargs):
    """
    Update and modify matter closing_group when item is changes
    """
    matter = instance.matter

    try:
        # get the current
        previous_instance = sender.objects.get(pk=instance.pk)

    except sender.DoesNotExist:
        #
        # Do nothing as the previous object does not exist
        #
        pass

    if previous_instance.status != instance.status:
        matter.actions.item_change_status(user=matter.lawyer,  # WHO is allowed to change status?
                                          item=instance,
                                          previous_status=previous_instance.status)

    logger.debug('Recieved item.pre_save:changed_status event: %s' % sender)
