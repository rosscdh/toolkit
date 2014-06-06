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

        with self.assertRaises(PermissionDenied):
            MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.customer,
                                        changing_user=self.lawyer).process()

    def test_matter_manage_participants_true(self):
        # prepare user with permission
        self.prepare_user({'workspace.manage_participants': True})

        MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.customer,
                                    changing_user=self.lawyer).process()

    def _test_permission(self, perm):
        permission_to_check = perm
        self.prepare_user({permission_to_check: True})
        self.assertTrue(self.lawyer.has_perm(permission_to_check, self.matter))
        self.prepare_user({permission_to_check: False})
        self.assertFalse(self.lawyer.has_perm(permission_to_check, self.matter))

    def test_matter_manage_items(self):
        self._test_permission('workspace.manage_items')