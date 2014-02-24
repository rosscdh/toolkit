# -*- coding: utf-8 -*-
"""
Item signals to handle various events that take place on save
"""
from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import Item

import logging
logger = logging.getLogger('django.request')


@receiver(pre_save, sender=Item, dispatch_uid='item.post_save.category')
def on_item_save_category(sender, instance, **kwargs):
    """
    Update and modify matter categories when item is changes
    """
    matter = instance.matter
    # get the current
    previous_instance = sender.objects.get(pk=instance.pk)

    # compare
    prev_cat = previous_instance.category
    new_cat = instance.category

    if prev_cat != new_cat:
      #
      # We want to remove the previous cat from the matter
      #
      matter.remove_category(prev_cat, instance=instance)

    # add the new cat to the matter
    matter.add_category(new_cat)
    # save the matter
    matter.save(update_fields=['data'])  # save the updated data where categories are stored

    logger.debug('Recieved item.pre_save:category event: %s' % sender)


@receiver(pre_save, sender=Item, dispatch_uid='item.post_save.closing_group')
def on_item_save_closing_group(sender, instance, **kwargs):
    """
    Update and modify matter closing_group when item is changes
    """
    matter = instance.matter
    # get the current
    previous_instance = sender.objects.get(pk=instance.pk)

    # compare
    prev_cg = previous_instance.closing_group
    new_cg = instance.closing_group

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