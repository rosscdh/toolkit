# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

import datetime


lawyer_complete_form = Signal(providing_args=['actor_name'])
lawyer_invite_customer = Signal(providing_args=['actor_name'])
customer_complete_form = Signal(providing_args=['actor_name'])
customer_print_and_sign = Signal(providing_args=['actor_name'])
mail_to_irs = Signal(providing_args=[])
irs_recieved = Signal(providing_args=[])
datestampped_copy_recieved = Signal(providing_args=['actor_name'])
copy_sent_to_lawyer = Signal(providing_args=['actor_name'])
copy_sent_to_accountant = Signal(providing_args=['actor_name'])


@receiver(lawyer_complete_form)
def on_lawyer_complete_form(sender, instance, actor_name, **kwargs):
    marker_name = 'lawyer_complete_form'
    # get the data markers
    markers = instance.data.get('markers', {})
    # set our key
    if marker_name not in markers:
        markers[marker_name] = {
            'date_of': datetime.datetime.utcnow(),
            'actor_name': actor_name
        }
        # update markers object @TODO race condition?
        instance.data['markers'] = markers
        # set the next status
        instance.status = instance.STATUS_83b.lawyer_invite_customer
        # save
        instance.save(update_fields=['status', 'data'])

@receiver(lawyer_invite_customer)
def on_lawyer_invite_customer(sender, instance, **kwargs):
    pass

@receiver(customer_complete_form)
def on_customer_complete_form(sender, instance, **kwargs):
    pass

@receiver(customer_print_and_sign)
def on_customer_print_and_sign(sender, instance, **kwargs):
    pass

@receiver(mail_to_irs)
def on_mail_to_irs(sender, instance, **kwargs):
    pass

@receiver(irs_recieved)
def on_irs_recieved(sender, instance, **kwargs):
    pass

@receiver(datestampped_copy_recieved)
def on_datestampped_copy_recieved(sender, instance, **kwargs):
    pass

@receiver(copy_sent_to_lawyer)
def on_copy_sent_to_lawyer(sender, instance, **kwargs):
    pass

@receiver(copy_sent_to_accountant)
def on_copy_sent_to_accountant(sender, instance, **kwargs):
    pass
