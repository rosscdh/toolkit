# -*- coding: utf-8 -*-
"""
Listen for events from various models

Please Note!!!!

These signals shoudl be connected bt NOT using the reciever decorator

post_save.connect(on_item_post_save, sender=Item) in the item.models
"""
from django.db.models.signals import post_save

# signal handlers for post_save:

def on_workspace_post_save(sender, instance, created, **kwargs):
    """
        The owning lawyer is the only one who can create, modify or delete the workspace, so this is possible.
    """
    if created:
        from toolkit.core.services.matter_activity import MatterActivityEventService
        MatterActivityEventService(instance).created_matter(lawyer=instance.lawyer)


def on_item_post_save(sender, instance, created, **kwargs):
    """
        At this moment only the layer can edit items. So this is possible.
    """
    if created:
        from toolkit.core.services.matter_activity import MatterActivityEventService
        MatterActivityEventService(instance.matter).created_item(user=instance.matter.lawyer, item=instance)
