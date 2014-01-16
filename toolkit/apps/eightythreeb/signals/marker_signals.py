# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

from toolkit.apps.workspace.signals import _update_marker

from ..markers import EightyThreeBSignalMarkers
from ..mailers import EightyThreeTrackingCodeEnteredEmail

import datetime

import logging
logger = logging.getLogger('django.request')

""" Sundry signals """
lawyer_complete_form = Signal(providing_args=['actor'])
lawyer_invite_customer = Signal(providing_args=['actor'])
customer_complete_form = Signal(providing_args=['actor'])
customer_download_pdf = Signal(providing_args=['actor'])
customer_print_and_sign = Signal(providing_args=['actor'])
copy_uploaded = Signal(providing_args=['actor'])

valid_usps_tracking_marker = Signal(providing_args=['actor']) #sent jsut before (in the same process) as the mail_to_irs_tracking_code
mail_to_irs_tracking_code = Signal(providing_args=['actor'])

irs_recieved = Signal(providing_args=[])
complete = Signal(providing_args=['actor'])


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_complete_form',
                       next_status=instance.STATUS.lawyer_invite_customer,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_invite_customer',
                       next_status=instance.STATUS.customer_complete_form,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_complete_form',
                       next_status=instance.STATUS.customer_download_pdf,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_download_pdf)
def on_customer_download_pdf(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        #if self.object.status <= self.object.STATUS.customer_download_pdf:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_download_pdf',
                       next_status=instance.STATUS.customer_print_and_sign,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_print_and_sign)
def on_customer_print_and_sign(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_print_and_sign',
                       next_status=instance.STATUS.copy_uploaded,
                       actor_name=actor_name,
                       instance=instance)


@receiver(copy_uploaded)
def on_copy_uploaded(sender, instance, actor, **kwargs):
    if instance.markers.current.can_perform_action(user=actor):
        actor_name = actor.get_full_name()
        _update_marker(marker_name='copy_uploaded',
                       next_status=instance.STATUS.mail_to_irs_tracking_code,
                       actor_name=actor_name,
                       instance=instance)


@receiver(valid_usps_tracking_marker)
def on_valid_usps_tracking_marker(sender, instance, actor, **kwargs):
    """
    This is a simple record signal and thus should bump to the next in line
    """
    actor_name = actor.get_full_name()

    marker_node = instance.markers.marker(val='mail_to_irs_tracking_code')
    if marker_node.is_complete is False:
        # send email
        mailer = EightyThreeTrackingCodeEnteredEmail(recipients=[(u.get_full_name(), u.email) for u in instance.workspace.participants.all()])
        mailer.process(instance=instance)

    _update_marker(marker_name='valid_usps_tracking_marker',
                   next_status=instance.STATUS.mail_to_irs_tracking_code,
                   actor_name=actor_name,
                   instance=instance,
                   tracking_code=kwargs.get('tracking_code'))


@receiver(mail_to_irs_tracking_code)
def on_mail_to_irs_tracking_code(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()

    marker_node = instance.markers.marker(val='mail_to_irs_tracking_code')
    if marker_node.is_complete is False:
        # send email
        mailer = EightyThreeTrackingCodeEnteredEmail(recipients=[(u.get_full_name(), u.email) for u in instance.workspace.participants.all()])
        mailer.process(instance=instance)

    _update_marker(marker_name='mail_to_irs_tracking_code',
                   next_status=instance.STATUS.irs_recieved,
                   actor_name=actor_name,
                   instance=instance)


@receiver(irs_recieved)
def on_irs_recieved(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    _update_marker(marker_name='irs_recieved',
                   next_status=instance.STATUS.complete,
                   actor_name=actor_name,
                   instance=instance)
    # Send the complete signal here
    complete.send(sender=sender, instance=instance, actor=actor)


@receiver(complete)
def on_complete(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    # Send the final event here
    _update_marker(marker_name='complete',
                   next_status=instance.STATUS.complete,
                   actor_name=actor_name,
                   instance=instance)
