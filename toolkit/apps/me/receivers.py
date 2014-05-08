# -*- coding: utf-8 -*-
import datetime
from django.dispatch import receiver
from django.utils.dateformat import format

from payments.signals import WEBHOOK_SIGNALS

from toolkit.core.services.analytics import AtticusFinch


@receiver(WEBHOOK_SIGNALS['charge.succeeded'])
def on_charge_succeeded(sender, event, **kwargs):
    user = event.customer.user

    data = event.message['data']
    amount = float(data['object']['amount']) / 100
    created = data['object']['created']
    time = format(datetime.datetime.fromtimestamp(int(created)), 'c')

    analytics = AtticusFinch()
    analytics.event('subscription.billed', amount='${0:.2f}'.format(amount), time=time, user=user)
    analytics.mixpanel_track_charge(amount=amount, time=time, user=user)


@receiver(WEBHOOK_SIGNALS['charge.refunded'])
def on_charge_refunded(sender, event, **kwargs):
    user = event.customer.user

    data = event.message['data']
    amount = float(data['object']['amount']) / 100
    created = data['object']['created']
    time = format(datetime.datetime.fromtimestamp(int(created)), 'c')

    analytics = AtticusFinch()
    analytics.event('subscription.refunded', amount='${0:.2f}'.format(amount), time=time, user=user)
    analytics.mixpanel_track_charge(amount=-amount, time=time, user=user)


@receiver(WEBHOOK_SIGNALS['charge.failed'])
def on_charge_failed(sender, event, **kwargs):
    user = event.customer.user

    data = event.message['data']
    amount = float(data['object']['amount']) / 100
    created = data['object']['created']
    time = format(datetime.datetime.fromtimestamp(int(created)), 'c')

    analytics = AtticusFinch()
    analytics.event('subscription.failed', amount='${0:.2f}'.format(amount), time=time, user=user)


@receiver(WEBHOOK_SIGNALS['customer.subscription.created'])
def on_subscription_created(sender, event, **kwargs):
    user = event.customer.user

    data = event.message['data']
    started = data['object']['start']
    time = format(datetime.datetime.fromtimestamp(int(started)), 'c')

    analytics = AtticusFinch()
    analytics.event('subscription.created', time=time, user=user)
