from django.core.exceptions import PermissionDenied
from django.test import TestCase

from toolkit.apps.matter.services.matter_permission import MatterUserPermissionService
from toolkit.apps.workspace.models import ROLES

from toolkit.casper.workflow_case import BaseScenarios


class PermissionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(PermissionTest, self).setUp()
        self.basic_workspace()
        # self.item = mommy.make('item.Item', matter=self.matter)

    def test_matter_manage_participants_false(self):
        # prepare user without permission
        self.prepare_user({'manage_participants': False})

        with self.assertRaises(PermissionDenied):
            MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.client,
                                        changing_user=self.lawyer).process()

    def test_matter_manage_participants_true(self):
        # prepare user with permission
        self.set_user_matter_perms(user=self.lawyer, manage_participants=True)

        MatterUserPermissionService(matter=self.matter, user=self.user, role=ROLES.client,
                                    changing_user=self.lawyer).process()

    def _test_permission(self, perm):
        permission_to_check = perm
        self.set_user_permissions(self.lawyer, {permission_to_check: True})
        self.assertTrue(self.lawyer.has_perm(permission_to_check, self.matter))
        self.set_user_permissions(self.lawyer, {permission_to_check: False})
        self.assertFalse(self.lawyer.has_perm(permission_to_check, self.matter))

    def test_matter_manage_items(self):
        self._test_permission('manage_items')