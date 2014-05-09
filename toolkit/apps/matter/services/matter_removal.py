# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

import logging
logger = logging.getLogger('django.request')


class MatterRemovalService(object):
    """
    Service to delete the whole matter
    """
    matter = None
    removing_user = None
    current_user = None

    def __init__(self, matter=None, removing_user=None):
        self.matter = matter
        self.removing_user = removing_user

    def process(self):
        if self.removing_user == self.matter.lawyer:
            #
            # Only the primary lawyer can delete the matter
            #
            self.matter.delete()
        else:
            logger.error(u'User %s is not the primary lawyer of the matter : %s' % (self.removing_user, self.matter))
            raise PermissionDenied('You are not the primary lawyer')
