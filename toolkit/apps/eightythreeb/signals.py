# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver
from django.db.models.signals import pre_save, post_save

from .models import EightyThreeB
from .markers import EightyThreeBSignalMarkers

import datetime

import logging
logger = logging.getLogger('django.request')


""" Primary signal used as wrapper for others """
base_83b_signal = Signal(providing_args=['actor'])
""" Sundry signals """
lawyer_complete_form = Signal(providing_args=['actor'])
lawyer_invite_customer = Signal(providing_args=['actor'])
customer_complete_form = Signal(providing_args=['actor'])
customer_download_pdf = Signal(providing_args=['actor'])
customer_print_and_sign = Signal(providing_args=['actor'])
copy_uploaded = Signal(providing_args=['actor'])
mail_to_irs_tracking_code = Signal(providing_args=['actor'])
irs_recieved = Signal(providing_args=[]) # no actor as its an aotumated callback
datestamped_copy_recieved = Signal(providing_args=['actor'])
complete = Signal(providing_args=['actor'])


@receiver(base_83b_signal)
def on_base_signal(sender, instance, actor, **kwargs):
    """
    Primary handler that is called and will calculate the current and
    previous instance marker status, and issue the appropriate signals
    """
    markers = EightyThreeBSignalMarkers()  # @TODO can refer to instance.markers ?

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


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor, **kwargs):
    if actor.profile.is_lawyer:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_complete_form',
                       next_status=instance.STATUS_83b.lawyer_invite_customer,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, actor, **kwargs):
    if actor.profile.is_lawyer:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='lawyer_invite_customer',
                       next_status=instance.STATUS_83b.customer_complete_form,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, actor, **kwargs):
    if actor.profile.is_customer:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_complete_form',
                       next_status=instance.STATUS_83b.customer_download_pdf,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_download_pdf)
def on_customer_download_pdf(sender, instance, actor, **kwargs):
    if actor.profile.is_customer:
        #if self.object.status <= self.object.STATUS_83b.customer_download_pdf:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_download_pdf',
                       next_status=instance.STATUS_83b.customer_print_and_sign,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_print_and_sign)
def on_customer_print_and_sign(sender, instance, actor, **kwargs):
    if actor.profile.is_customer:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='customer_print_and_sign',
                       next_status=instance.STATUS_83b.copy_uploaded,
                       actor_name=actor_name,
                       instance=instance)

@receiver(copy_uploaded)
def on_copy_uploaded(sender, instance, actor, **kwargs):
    if actor.profile.is_customer:
        actor_name = actor.get_full_name()
        _update_marker(marker_name='copy_uploaded',
                       next_status=instance.STATUS_83b.mail_to_irs_tracking_code,
                       actor_name=actor_name,
                       instance=instance)


@receiver(mail_to_irs_tracking_code)
def on_mail_to_irs_tracking_code(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    _update_marker(marker_name='mail_to_irs_tracking_code',
                   next_status=instance.STATUS_83b.irs_recieved,
                   actor_name=actor_name,
                   instance=instance)


@receiver(irs_recieved)
def on_irs_recieved(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    _update_marker(marker_name='irs_recieved',
                   next_status=instance.STATUS_83b.datestamped_copy_recieved,
                   actor_name=actor_name,
                   instance=instance)


@receiver(datestamped_copy_recieved)
def on_datestamped_copy_recieved(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    _update_marker(marker_name='datestamped_copy_recieved',
                   next_status=instance.STATUS_83b.complete,
                   actor_name=actor_name,
                   instance=instance)
    # Send the complete signal here
    complete.send(sender=sender, instance=instance, actor=actor)

@receiver(complete)
def on_complete(sender, instance, actor, **kwargs):
    actor_name = actor.get_full_name()
    # Send the final event here
    _update_marker(marker_name='complete',
                   next_status=instance.STATUS_83b.complete,
                   actor_name=actor_name,
                   instance=instance)


@receiver(pre_save, sender=EightyThreeB, dispatch_uid='83b.ensure_dates')
def ensure_dates(sender, **kwargs):
    """
    signal to handle creating the workspace slug
    """
    instance = kwargs.get('instance')

    if instance.data.get('date_of_property_transfer', None) is not None:
      if instance.transfer_date in [None, '']:
        instance.transfer_date = instance.get_transfer_date()

      if instance.filing_date in [None, '']:
        instance.filing_date = instance.get_filing_date()


@receiver(post_save, sender=EightyThreeB, dispatch_uid='83b.ensure_83b_user_in_workspace_participants')
def ensure_83b_user_in_workspace_participants(sender, **kwargs):
    eightythreeb = kwargs.get('instance')
    created = kwargs.get('created', False)

    user = eightythreeb.user
    workspace = eightythreeb.workspace

    # when we have a new one
    if user not in workspace.participants.all():
        workspace.participants.add(user)

