# -*- coding: utf-8 -*-
from toolkit.core.permisson import AdvancedParticipantsPermissionLogic

PERMISSION_LOGICS = (
    ('item.Item', AdvancedParticipantsPermissionLogic(field_name='matter__participants',
                                                      any_permission=False,
                                                      change_permission=False,
                                                      read_permission=True,
                                                      delete_permission=False)),
)