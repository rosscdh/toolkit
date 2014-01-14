# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

from .markers import EngagementLetterSignalMarkers

import datetime

import logging
logger = logging.getLogger('django.request')


""" Primary signal used as wrapper for others """
base_signal = Signal(providing_args=['actor'])
""" Sundry signals """
lawyer_setup_template = Signal(providing_args=['actor'])
lawyer_complete_form = Signal(providing_args=['actor'])
lawyer_invite_customer = Signal(providing_args=['actor'])
customer_complete_form = Signal(providing_args=['actor'])
customer_sign_and_send = Signal(providing_args=['actor'])
customer_download_letter = Signal(providing_args=['actor'])
lawyer_download_letter = Signal(providing_args=['actor'])
complete = Signal(providing_args=['actor'])


@receiver(base_signal)
def on_base_signal(sender, instance, actor, **kwargs):
    """
    Primary handler that is called and will calculate the current and
    previous instance marker status, and issue the appropriate signals
    """
    markers = instance.markers

    # if we are provided a kwargs "name" then use that.. otherwise use the current instance marker
    marker_node = markers.marker(val=kwargs.get('name', instance.status))

    if hasattr(marker_node, 'issue_signals'):
        marker_node.issue_signals(request=sender, instance=instance, actor=actor)
    else:
        logger.error('Requested signal marker "%s" has no issue_signals method' % marker_node)


def _update_marker(marker_name, next_status, actor_name, instance, **kwargs):
    """
    Shared process used by signals to perform status updates
    """
    # get the data markers
    markers = instance.data.get('markers', {})
    # capture fields to update
    update_fields = []

    # set our key
    #if instance.status < next_status:

    kwargs.update({
        'date_of': datetime.datetime.utcnow(),
        'actor_name': actor_name
    })
    markers[marker_name] = kwargs

    # update markers object @TODO race condition?
    instance.data['markers'] = markers

    update_fields.append('data')

    # set the next status
    # @BUSINESSRULE only update if the current status is less than our reqeusted status
    if instance.status < next_status:
        instance.status = next_status
        update_fields.append('status')

    # save
    instance.save(update_fields=update_fields)


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
      # @TODO if thelawyer has downloaded AND the customer has downloaded then its complete
      actor_name = actor.get_full_name()
      # Send the final event here
      _update_marker(marker_name='complete',
                     next_status=instance.markers.next.val,
                     actor_name=actor_name,
                     instance=instance)
