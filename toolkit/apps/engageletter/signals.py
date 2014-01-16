# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

from toolkit.apps.workspace.signals import _update_marker

import logging
logger = logging.getLogger('django.request')


""" Sundry signals """
lawyer_setup_template = Signal(providing_args=['actor'])
lawyer_complete_form = Signal(providing_args=['actor'])
lawyer_invite_customer = Signal(providing_args=['actor'])
customer_complete_form = Signal(providing_args=['actor'])
customer_sign_and_send = Signal(providing_args=['actor'])
customer_download_letter = Signal(providing_args=['actor'])
lawyer_download_letter = Signal(providing_args=['actor'])
complete = Signal(providing_args=['actor'])


@receiver(lawyer_setup_template)
def on_lawyer_setup_template(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_setup_template',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_complete_form',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_invite_customer',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_complete_form',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_sign_and_send)
def on_customer_sign_and_send(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_sign_and_send',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_download_letter)
def on_customer_download_letter(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_download_letter',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)
        # @TODO issue complete signal


@receiver(lawyer_download_letter)
def on_lawyer_download_letter(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_download_letter',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)
        # @TODO issue complete signal


@receiver(complete)
def on_complete(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        # @TODO if thelawyer has downloaded AND the customer has downloaded
        # then its complete
        actor_name = actor.get_full_name()
        # Send the final event here
        _update_marker(marker_name='complete',
                       next_status=instance.markers.next.val,
                       actor_name=actor_name,
                       instance=instance)
