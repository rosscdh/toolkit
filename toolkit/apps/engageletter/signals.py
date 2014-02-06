# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

from toolkit.apps.workspace.signals import _update_marker

from hello_sign.signals import hellosign_webhook_event_recieved

import logging
logger = logging.getLogger('django.request')


""" Sundry signals """
lawyer_setup_template = Signal(providing_args=['actor'])
lawyer_complete_form = Signal(providing_args=['actor'])
lawyer_review_letter_text = Signal(providing_args=['actor'])
lawyer_invite_customer = Signal(providing_args=['actor'])
customer_complete_form = Signal(providing_args=['actor'])
customer_sign_and_send = Signal(providing_args=['actor'])
lawyer_sign = Signal(providing_args=['actor'])
complete = Signal(providing_args=['actor'])


@receiver(lawyer_setup_template)
def on_lawyer_setup_template(sender, instance, actor, **kwargs):
    marker_name = 'lawyer_setup_template'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor, **kwargs):
    marker_name = 'lawyer_complete_form'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_review_letter_text)
def on_lawyer_review_letter_text(sender, instance, actor, **kwargs):
    marker_name = 'lawyer_review_letter_text'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, actor, **kwargs):
    marker_name = 'lawyer_invite_customer'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, actor, **kwargs):
    marker_name = 'customer_complete_form'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_sign_and_send)
def on_customer_sign_and_send(sender, instance, actor, **kwargs):
    marker_name = 'customer_sign_and_send'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_sign)
def on_lawyer_sign(sender, instance, actor, **kwargs):
    marker_name = 'lawyer_sign'
    marker = instance.markers.marker(marker_name)

    if marker.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name=marker_name,
                       next_status=marker.next_marker.val,
                       actor_name=actor_name,
                       instance=instance)

@receiver(complete)
def on_complete(sender, instance, actor, **kwargs):
    marker_name = 'complete'
    marker = instance.markers.marker(marker_name)
    actor_name = actor.get_full_name()
    # Send the final event here
    _update_marker(marker_name=marker_name,
                   next_status=instance.STATUS.complete,
                   actor_name=actor_name,
                   instance=instance)


@receiver(hellosign_webhook_event_recieved)
def on_hellosign_webhook_event_recieved(sender, hellosign_log, signature_request_id, hellosign_request, event_type, data, **kwargs):
  import pprint
  import json
  logging.info('Recieved event: %s for request: %s' % (event_type, hellosign_request,))
  logging.info(data)
  PPP = pprint.PrettyPrinter(indent=4)
  PPP.pprint(json.dumps(data))

