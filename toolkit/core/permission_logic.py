# -*- coding: utf-8 -*-
from permission.logics.base import PermissionLogic

from toolkit.apps.workspace.models import WorkspaceParticipants

import re
import logging

logger = logging.getLogger('django.request')
permission_pattern = re.compile('^(\w*)\.([a-zA-Z_]*)_([a-zA-Z]*)$')


class MatterPermissionLogic(PermissionLogic):
    """
    TODO:
    load permissions from participants-through-m2m and it's data-json
    """
    def __init__(self,
                 any_permission=None,
                 change_permission=None,
                 delete_permission=None):

        self.any_permission = any_permission
        self.change_permission = change_permission
        self.delete_permission = delete_permission

    def has_perm(self, user_obj, perm, obj=None):
        """
        Check if user have permission (of object)

        If the user_obj is not authenticated, it return ``False``.

        If no object is specified, it return ``True`` when the corresponding
        permission was specified to ``True`` (changed from v0.7.0).


        If an object is specified, it will return ``True`` if the user is
        permitted, based on WorkspaceUser-table.

        Parameters
        ----------
        user_obj : django user model instance
            A django user model instance which be checked
        perm : string
            `app_label.codename` formatted permission string
        obj : None or django model instance
            None or django model instance for object permission

        Returns
        -------
        boolean
            Wheter the specified user have specified permission (of specified
            object).
        """
        if not user_obj.is_authenticated():
            return False  # Always return false if we are not logged in

        # replace the passed in models app_label 'workspace.' as the following line adds it back
        # note the additions of the . seperator
        perm = perm.replace('%s.' %WorkspaceParticipants._meta.app_label, '')
        #permission_name = self.get_full_permission_string(perm)

        if obj is None:
            # object permission without obj should return True
            # Ref: https://code.djangoproject.com/wiki/RowLevelPermissions
            if self.any_permission:
                return True

            if self.change_permission and perm == permission_name:
                return True
            return False

        elif user_obj.is_active:

            try:
                matter_participant = WorkspaceParticipants.objects.get(workspace=obj, user=user_obj)
            except WorkspaceParticipants.DoesNotExist:
                return False

            return matter_participant.permissions.get(perm, False)

        return False
