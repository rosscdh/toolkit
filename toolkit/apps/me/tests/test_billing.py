# -*- coding: utf-8 -*-
import decimal
import json
import mock
import stripe

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from payments.models import Charge, Customer, CurrentSubscription

from toolkit.casper.workflow_case import BaseScenarios

from ..views import PaymentListView, PlanListView


class PaymentListViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PaymentListViewTest, self).setUp()
        self.basic_workspace()

    def test_get_queryset(self):
        customer1 = Customer.objects.create(stripe_id='cus_1', user=self.lawyer)
        customer2 = Customer.objects.create(stripe_id='cus_2', user=self.user)

        charge1 = Charge.objects.create(customer=customer1, stripe_id='ch_1')
        charge2 = Charge.objects.create(customer=customer1, stripe_id='ch_2')
        charge3 = Charge.objects.create(customer=customer2, stripe_id='ch_3')
        charge4 = Charge.objects.create(customer=customer2, stripe_id='ch_4')

        self.client.login(username=self.lawyer.username, password=self.password)
        response = self.client.get(reverse('me:payment-list'))

        data = response.context['object_list']
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], charge2)
        self.assertEqual(data[1], charge1)


class PlanListViewTest(TestCase):
    def test_get_context_data(self):
        data = PlanListView().get_context_data()
        self.assertEqual(len(data['object_list']), 1)
        self.assertEqual(data['object_list'][0], settings.PAYMENTS_PLANS['early-bird-monthly'])


class PlanChangeViewTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PlanChangeViewTest, self).setUp()
        self.basic_workspace()

        customer = Customer.objects.create(
            stripe_id='cus_1',
            user=self.lawyer
        )
        CurrentSubscription.objects.create(
            customer=customer,
            plan='pro',
            quantity=1,
            start=timezone.now(),
            status='active',
            cancel_at_period_end=False,
            amount=decimal.Decimal('19.99')
        )

    @mock.patch('payments.models.Customer.subscribe')
    def test_change_plan_with_subscription(self, subscribe_mock):
        self.client.login(username=self.lawyer.username, password=self.password)
        response = self.client.post(
            reverse('me:plan-change', kwargs={'plan': 'early-bird-monthly'}),
            {'plan': 'early-bird-monthly'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(subscribe_mock.call_count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'redirect': True,
            'url': reverse('me:welcome')
        })

    @mock.patch('payments.models.Customer.subscribe')
    def test_change_plan_no_subscription(self, subscribe_mock):
        self.lawyer.customer.current_subscription.delete()
        self.client.login(username=self.lawyer.username, password=self.password)
        response = self.client.post(
            reverse('me:plan-change', kwargs={'plan': 'early-bird-monthly'}),
            {'plan': 'early-bird-monthly'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(subscribe_mock.call_count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'redirect': True,
            'url': reverse('me:welcome')
        })

    @mock.patch('payments.models.Customer.subscribe')
    def test_change_plan_invalid_form(self, subscribe_mock):
        self.client.login(username=self.lawyer.username, password=self.password)
        response = self.client.post(
            reverse('me:plan-change', kwargs={'plan': 'invalid-plan'}),
            {'plan': 'invalid-plan'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(subscribe_mock.call_count, 0)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content), {
            'error': { 'message': 'No plan found matching the id: invalid-plan' }
        })

    @mock.patch('payments.models.Customer.subscribe')
    def test_change_plan_stripe_error(self, subscribe_mock):
        subscribe_mock.side_effect = stripe.StripeError(
            "Bad card",
            "Param",
            "CODE"
        )
        self.client.login(username=self.lawyer.username, password=self.password)
        response = self.client.post(
            reverse('me:plan-change', kwargs={'plan': 'early-bird-monthly'}),
            {'plan': 'early-bird-monthly'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(subscribe_mock.call_count, 1)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content), {
            'error': { 'message': 'Bad card' }
        })
