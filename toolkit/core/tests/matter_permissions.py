# -*- coding: utf-8 -*-
from django.test import TestCase

from toolkit.casper.workflow_case import BaseScenarios
from toolkit.apps.workspace.models import WorkspaceParticipants

from model_mommy import mommy


class MatterPermissionTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterPermissionTest, self).setUp()
        self.basic_workspace()

    def test_user_has_monkeypatched_method(self):
        """
        matter_permissions returns the permission object for a users matter
        """
        self.assertTrue(hasattr(self.user, 'matter_permissions'))
        self.assertTrue(hasattr(self.lawyer, 'matter_permissions'))

    def test_matter_owner_default_permissions(self):
        self.assertEqual(self.lawyer.matter_permissions(matter=self.matter).permissions, WorkspaceParticipants.MATTER_OWNER_PERMISSIONS)

    def test_user_default_permissions(self):
        self.assertEqual(self.user.matter_permissions(matter=self.matter).permissions, WorkspaceParticipants.UNPRIVILEGED_USER_PERMISSIONS)

    def test_user_with_no_access_to_matter(self):
        user_with_no_access = mommy.make('auth.User', username='no-access', email='noaccess@lawpal.com')
        self.assertEqual(user_with_no_access.matter_permissions(matter=self.matter).permissions, WorkspaceParticipants.ANONYMOUS_USER_PERMISSIONS)

    def test_override_of_permissions(self):
        perm = self.user.matter_permissions(matter=self.matter)

        test_permissions = WorkspaceParticipants.MATTER_OWNER_PERMISSIONS.copy()
        test_permissions.update({'monkey': True, })

        perm.permissions = test_permissions
        # assert the keys are equal
        self.assertItemsEqual(perm.permissions.keys(), WorkspaceParticipants.MATTER_OWNER_PERMISSIONS.keys())
        # assert that monkey which is not a valid permission did not go in
        self.assertTrue('monkey' not in perm.permissions.keys())

    def test_update_permissions(self):
        perm = self.user.matter_permissions(matter=self.matter)
        self.assertTrue(perm.permissions.get('manage_participants') is False)

        perm.update_permissions(monkey=True, manage_participants=True)

        self.assertTrue('monkey' not in perm.permissions.keys())
        self.assertTrue(perm.permissions.get('manage_participants') is True)

    def test_reset_permissions(self):
        perm = self.user.matter_permissions(matter=self.matter)
        self.assertTrue(perm.permissions.get('manage_participants') is False)

        perm.update_permissions(manage_participants=True)
        self.assertTrue(perm.permissions.get('manage_participants') is True)

        perm.reset_permissions()

        self.assertTrue(perm.permissions.get('manage_participants') is False)
        self.assertItemsEqual(perm.permissions.keys(), WorkspaceParticipants.UNPRIVILEGED_USER_PERMISSIONS.keys())

    def test_display_role(self):
        perm = self.user.matter_permissions(matter=self.matter)
        self.assertEqual(perm.display_role, WorkspaceParticipants.ROLES.get_desc_by_value(WorkspaceParticipants.ROLES.client))

        perm = self.lawyer.matter_permissions(matter=self.matter)
        self.assertEqual(perm.display_role, WorkspaceParticipants.ROLES.get_desc_by_value(WorkspaceParticipants.ROLES.owner))

    def test_has_permission(self):
        perm = self.user.matter_permissions(matter=self.matter)
        self.assertTrue(perm.has_permission(manage_items=True))
        # clients do not by default have manage_participants permissions
        self.assertFalse(perm.has_permission(manage_participants=True))
        self.assertTrue(perm.has_permission(manage_participants=False))


