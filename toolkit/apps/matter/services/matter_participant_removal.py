# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

import logging
logger = logging.getLogger('django.request')


class MatterParticipantRemovalService(object):
    """
    Service to remove a participant from the matter
    """
    matter = None
    removing_user = None
    current_user = None

    def __init__(self, matter=None, removing_user=None):
        self.matter = matter
        self.removing_user = removing_user

    def process(self, user_to_remove=None):
        if user_to_remove in self.matter.participants.all():
            #
            # all participants can remove themselves; laywers can remove other participants but not the primary lawyer
            #
            if self.removing_user == user_to_remove:

                self.matter.participants.remove(user_to_remove)
                self.matter.actions.user_stopped_participating(user=user_to_remove)

            elif self.removing_user.profile.is_lawyer and self.matter.lawyer != user_to_remove:

                self.matter.participants.remove(user_to_remove)
                self.matter.actions.removed_matter_participant(matter=self.matter, removing_user=self.removing_user, removed_user=user_to_remove)

            else:
                logger.error(u'User %s tried to remove the participant: %s in the matter: %s but were not the primary lawyer' % (self.current_user, user_to_remove, self.matter))
                raise PermissionDenied('You are not allowed to remove a participant of this matter')
        else:
            logger.error(u'User %s is not the participating in matter : %s' % (user_to_remove, self.matter))
            raise PermissionDenied('This user is not a participant of this matter')
