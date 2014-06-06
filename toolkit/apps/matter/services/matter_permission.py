# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

import logging
from toolkit.apps.workspace.models import MatterParticipant

logger = logging.getLogger('django.request')


class MatterUserPermissionService(object):
    """
    Service to add user to matter (as participant) and/or modify its permissions

    Adding:
    MatterUserPermissionService(matter=self.matter,
                                changed_user=self.lawyer,
                                changing_user=self.lawyer,
                                permissions={"workspace.manage_participants": True}  # only given permissions are changed
                                ).process()

    override is ONLY used for initialisation

    permissions need to be in this structure:
    {'Model.permission': true}
    {'Workspace.manage_participants': false}
    """
    matter = None
    changed_user = None
    changing_user = None
    matter_participant_obj = None
    override = False

    def __init__(self, matter, role, user, changing_user):
        self.matter = matter
        self.role = role
        self.changed_user = user
        self.changing_user = changing_user

    def get_matter_participant(self):
        # returns unsaved MatterUser
        try:
            matter_participant = MatterParticipant.objects.get(matter=self.matter,
                                                               user=self.changed_user)
            matter_participant.role = self.role
        except MatterParticipant.DoesNotExist:
            matter_participant = MatterParticipant(matter=self.matter,
                                                   user=self.changed_user,
                                                   role=self.role)
        return matter_participant

    @property
    def matter_participant(self):
        if self.matter_participant_obj is None:
            self.matter_participant_obj = self.get_matter_participant()
        return self.matter_participant_obj

    @property
    def is_allowed(self):
        necessary_permission = 'workspace.manage_participants'
        if not self.changing_user.has_perm(necessary_permission, self.matter):
            logger.error(u'User %s does not have permission: %s in matter: %s' %
                         (self.changing_user, necessary_permission, self.matter))
            raise PermissionDenied('You are missing a permission: %s' % necessary_permission)
        return True

    def reset_permissions(self, permissions):
        permission_dict = {}
        if permissions:
            for key, value in permissions.items():
                permission_dict[key] = value
        return permission_dict

    def process(self, permissions=None):
        if self.is_allowed:
            matter_participant = self.matter_participant

            permission_dict = self.reset_permissions(permissions)

            if matter_participant.data.get('permissions', {}) != permission_dict:
                matter_participant.data['permissions'] = permission_dict

            if matter_participant.pk:
                matter_participant.save(update_fields=['data', 'role'])
            else:
                matter_participant.save()

    def delete(self):
        if self.is_allowed:
            self.matter_participant.delete()


class MightyMatterUserPermissionService(MatterUserPermissionService):
    @property
    def is_allowed(self):
        return True