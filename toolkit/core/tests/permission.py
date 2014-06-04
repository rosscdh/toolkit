from django.core.exceptions import PermissionDenied
from django.test import TestCase

from model_mommy import mommy
from toolkit.apps.matter.services.matter_permission import MightyMatterUserPermissionService, \
    MatterUserPermissionService
from toolkit.apps.workspace.models import ROLES

from toolkit.casper.workflow_case import BaseScenarios


class PermissionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PermissionTest, self).setUp()
        self.basic_workspace()
        # self.item = mommy.make('item.Item', matter=self.matter)

    def prepare_user(self, permissions, role=ROLES.lawyer):
        MightyMatterUserPermissionService(matter=self.matter, user=self.lawyer, role=role,
                                          changing_user=self.lawyer).process(permissions)

    def test_matter_manage_participants_false(self):
        # prepare user without permission
        self.prepare_user({'workspace.manage_participants': False})

        try:
            MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.customer,
                                        changing_user=self.lawyer).process()
            success = True
        except PermissionDenied:
            success = False

        self.assertFalse(success)

    def test_matter_manage_participants_true(self):
        # prepare user without permission
        self.prepare_user({'workspace.manage_participants': True})

        try:
            MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.customer,
                                        changing_user=self.lawyer).process()
            success = True
        except PermissionDenied:
            success = False

        self.assertTrue(success)
        # import pdb;pdb.set_trace()

    #
    # def test_add_perm(self):
    #     self.assertEqual(self.lawyer.has_perm('workspace.manage_participants', self.matter), True)