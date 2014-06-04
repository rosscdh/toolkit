# -*- coding: utf-8 -*-

import logging
import re

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from permission.conf import settings
from permission.logics.base import PermissionLogic
from permission.utils.field_lookup import field_lookup

from toolkit.apps.workspace.models import MatterParticipant


logger = logging.getLogger('django.request')
permission_pattern = re.compile('^(\w*)\.([a-zA-Z_]*)_([a-zA-Z]*)$')


class MatterPermissionLogic(PermissionLogic):
    """
    TODO:
    load permissions from participants-through-m2m and it's data-json
    """
    def __init__(self):
        pass

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
            return False

        permission_name = self.get_full_permission_string(perm)

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
                matter_participant = MatterParticipant.objects.get(matter=obj, user=user_obj)
            except MatterParticipant.DoesNotExist:
                return False

            return matter_participant.data.get('permissions', {}).get(perm, False)

            # # key has this scheme: "%s.%s_%s" % (app_label, perm, model_name)
            # m = re.search(permission_pattern, permission_name)
            #
            # app_label = m.group(1)
            # perm = m.group(2)
            # model_name = m.group(3)
            # try:
            #     permission = Permission.objects.get(
            #         codename=perm,
            #         content_type=ContentType.objects.get(app_label=app_label, model=model_name)
            #     )
            # except Permission.DoesNotExist:
            #     logger.critical(u'Permission used which does not exist: %s' % permission_name)
            #     raise PermissionDenied('You are using a broken permission: %s' % permission_name)
            #
        return False