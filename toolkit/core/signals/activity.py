# -*- coding: utf-8 -*-
"""
Listen for events from various models

Please Note!!!!

These signals shoudl be connected bt NOT using the reciever decorator

post_save.connect(on_item_post_save, sender=Item) in the item.models
"""

# signal handlers for post_save:


def on_workspace_post_save(sender, instance, created, **kwargs):
    """
        The owning lawyer is the only one who can create, modify or delete the workspace, so this is possible.
    """
    if created:
        matter = instance
        matter.actions.created_matter(lawyer=matter.lawyer)


def on_workspace_pre_save(sender, instance, created, **kwargs):
    pass
    # TODO check for new participants and send signal


def on_item_post_save(sender, instance, created, **kwargs):
    """
        At this moment only the layer can edit items. So this is possible.
    """
    if created:
        matter = instance.matter
        matter.actions.created_item(user=matter.lawyer, item=instance)
