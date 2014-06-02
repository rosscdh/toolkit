# -*- coding: utf-8 -*-
from toolkit.core.permisson import AdvancedParticipantsPermissionLogic

PERMISSION_LOGICS = (
    ('item.Item', AdvancedParticipantsPermissionLogic(field_name='matter__participants',
                                                      any_permission=None,
                                                      change_permission=None,
                                                      read_permission=None,
                                                      delete_permission=None)),
)