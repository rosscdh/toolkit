# -*- coding: utf-8 -*-
import json
from django.core.exceptions import PermissionDenied

import logging
from toolkit.apps.workspace.models import MatterUser

logger = logging.getLogger('django.request')


class MatterUserPermissionService(object):
    """
    Service to add user to matter (as participant) and/or modify its permissions

    Adding:
    MatterUserPermissionService(matter=self.matter,
                                changed_user=self.lawyer,
                                changing_user=self.lawyer,
                                permissions='{"workspace.manage_participants": true}'  # only given permissions are changed
                                ).process()

    override is ONLY used for initialisation

    permissions need to be in this structure:
    {'Model.permission': true}
    {'Workspace.manage_participants': false}
    """
    matter = None
    changed_user = None
    changing_user = None
    matter_user_obj = None
    override = False

    def __init__(self, matter=None, changed_user=None, changing_user=None, permissions=None, override=False):
        self.matter = matter
        self.changed_user = changed_user
        self.changing_user = changing_user
        self.permissions = permissions
        self.override = override

    def set_permissions(self, permissions):
        self.permissions = permissions

    def delete_permissions(self):
        self.permissions = '{}'

    def get_matter_user(self):
        # returns (newly created) MatterUser
        matter_user, created = MatterUser.objects.get_or_create(matter=self.matter, user=self.changed_user)
        return matter_user

    @property
    def matter_user(self):
        if self.matter_user_obj is None:
            self.matter_user_obj = self.get_matter_user()
        return self.matter_user_obj

    def process(self):
        necessary_permission = 'workspace.manage_participants'
        if not (self.changing_user.has_perm(necessary_permission, self.matter) or self.override):
            logger.error(u'User %s does not have permission: %s in matter: %s' %
                         (self.changing_user, necessary_permission, self.matter))
            raise PermissionDenied('You are missing a permission: %s' % necessary_permission)

        matter_user = self.matter_user

        if self.permissions:
            permission_dict = matter_user.data.get('permissions', {})

            for key, value in json.loads(self.permissions).items():
                permission_dict[key] = value

            if matter_user.data.get('permissions', {}) != permission_dict:
                matter_user.data['permissions'] = permission_dict
            matter_user.save(update_fields=['data'])
