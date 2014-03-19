# -*- coding: utf-8 -*-
from abridge.services import AbridgeService


class LawPalAbridgeService(object):
    """
    Wrapper for wrapping the abridge service
    allows us to disable it in testing and based on settings
    """
    ABRIDGE_ENABLED = False
    service = None

    def __init__(self, user, ABRIDGE_ENABLED=False, **kwargs):
        self.ABRIDGE_ENABLED = ABRIDGE_ENABLED

        assert user.__class__.__name__ == 'User', 'user must be a auth.User object'

        self.service = None  # reset to None by default
        if self.ABRIDGE_ENABLED:  # check if enabled
            self.service = AbridgeService(user=user)

    def create_event(self, content_group, content, **kwargs):
        if self.service is not None and self.ABRIDGE_ENABLED is True:
            self.service.create_event(content_group=content_group,
                                      content=content)
