# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

import datetime


lawyer_complete_form = Signal(providing_args=['actor_name'])
lawyer_invite_customer = Signal(providing_args=['actor_name'])
customer_complete_form = Signal(providing_args=['actor_name'])
customer_download_pdf = Signal(providing_args=['actor_name'])
customer_print_and_sign = Signal(providing_args=['actor_name'])
mail_to_irs_tracking_code = Signal(providing_args=[])
irs_recieved = Signal(providing_args=[])
datestampped_copy_recieved = Signal(providing_args=['actor_name'])
copy_sent_to_lawyer = Signal(providing_args=['actor_name'])
copy_sent_to_accountant = Signal(providing_args=['actor_name'])


def _update_marker(marker_name, marker_status, actor_name, instance):
    # get the data markers
    markers = instance.data.get('markers', {})
    # capture fields to update
    update_fields = []

    # set our key
    if instance.status < marker_status:

        markers[marker_name] = {
            'date_of': datetime.datetime.utcnow(),
            'actor_name': actor_name
        }

        # update markers object @TODO race condition?
        instance.data['markers'] = markers

        update_fields.append('data')

        # set the next status
        # @BUSINESSRULE only update if the current status is less than our reqeusted status
        if instance.status < marker_status:
            instance.status = marker_status
            update_fields.append('status')

        # save
        instance.save(update_fields=update_fields)


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor_name, **kwargs):
    if sender.profile.is_lawyer:
        _update_marker(marker_name='lawyer_complete_form',
                       marker_status=instance.STATUS_83b.lawyer_invite_customer,
                       actor_name=actor_name,
                       instance=instance)


@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, **kwargs):
    if sender.profile.is_lawyer:
        actor_name = sender.email
        _update_marker(marker_name='lawyer_invite_customer',
                       marker_status=instance.STATUS_83b.customer_complete_form,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, **kwargs):
    if sender.profile.is_customer:
        actor_name = sender.email
        _update_marker(marker_name='customer_complete_form',
                       marker_status=instance.STATUS_83b.customer_download_pdf,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_download_pdf)
def on_customer_download_pdf(sender, instance, **kwargs):
    if sender.profile.is_customer:
        actor_name = sender.email
        _update_marker(marker_name='customer_download_pdf',
                       marker_status=instance.STATUS_83b.customer_print_and_sign,
                       actor_name=actor_name,
                       instance=instance)


@receiver(customer_print_and_sign)
def on_customer_print_and_sign(sender, instance, **kwargs):
    if sender.profile.is_customer:
        actor_name = sender.email
        _update_marker(marker_name='customer_print_and_sign',
                       marker_status=instance.STATUS_83b.mail_to_irs_tracking_code,
                       actor_name=actor_name,
                       instance=instance)


@receiver(mail_to_irs_tracking_code)
def on_mail_to_irs_tracking_code(sender, instance, **kwargs):
    actor_name = sender.email
    _update_marker(marker_name='mail_to_irs_tracking_code',
                   marker_status=instance.STATUS_83b.irs_recieved,
                   actor_name=actor_name,
                   instance=instance)


@receiver(irs_recieved)
def on_irs_recieved(sender, instance, **kwargs):
    actor_name = sender.email
    _update_marker(marker_name='irs_recieved',
                   marker_status=instance.STATUS_83b.datestampped_copy_recieved,
                   actor_name=actor_name,
                   instance=instance)


@receiver(datestampped_copy_recieved)
def on_datestampped_copy_recieved(sender, instance, **kwargs):
    actor_name = sender.email
    _update_marker(marker_name='datestampped_copy_recieved',
                   marker_status=instance.STATUS_83b.copy_sent_to_lawyer,
                   actor_name=actor_name,
                   instance=instance)


@receiver(copy_sent_to_lawyer)
def on_copy_sent_to_lawyer(sender, instance, **kwargs):
    actor_name = sender.email
    _update_marker(marker_name='copy_sent_to_lawyer',
                   marker_status=instance.STATUS_83b.copy_sent_to_accountant,
                   actor_name=actor_name,
                   instance=instance)


@receiver(copy_sent_to_accountant)
def on_copy_sent_to_accountant(sender, instance, **kwargs):
    actor_name = sender.email
    _update_marker(marker_name='copy_sent_to_accountant',
                   marker_status=instance.STATUS_83b.complete,
                   actor_name=actor_name,
                   instance=instance)
