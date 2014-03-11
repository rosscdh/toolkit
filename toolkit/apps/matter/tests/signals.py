from django.core import mail
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

from ..signals import participant_added


class ParticipantAddedTest(BaseScenarios, TestCase):
    def setUp(self):
        super(ParticipantAddedTest, self).setUp()
        self.basic_workspace()

    def test_sends_email_to_added_participant(self):
        participant = mommy.make('auth.User', first_name='New', last_name='Participant', email='test+participant@lawpal.com')

        # No email has been sent yet
        self.assertEqual(0, len(mail.outbox))

        # Check the email was sent
        participant_added(self, self.matter, participant, self.lawyer)
        self.assertEqual(len(mail.outbox), 1)

        # Test parts of the email
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'You have been invited to the Lawpal (test) matter on LawPal')
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+participant@lawpal.com'])
        self.assertEqual(email.from_email, u'Lawyer Test (via LawPal) support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': self.lawyer.email})

