# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import PermissionDenied

from toolkit.apps.matter.signals import PARTICIPANT_DELETED, USER_STOPPED_PARTICIPATING
from toolkit.apps.workspace.models import WorkspaceParticipants, ROLES


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
                self.matter.remove_participant(user=user_to_remove)
                USER_STOPPED_PARTICIPATING.send(sender=self,
                                                matter=self.matter,
                                                participant=user_to_remove)

            # either user has manage_participants or he removes a client and has manage_clients.
            # additionaly he cannot remove the primary lawyer (last 'and')
            elif (self.removing_user.matter_permissions(matter=self.matter).has_permission(manage_participants=True) is True
                    or user_to_remove.matter_permissions(matter=self.matter).role == ROLES.client
                       and self.removing_user.matter_permissions(matter=self.matter).has_permission(manage_clients=True)) \
                    and self.matter.lawyer != user_to_remove:
                self.matter.remove_participant(user=user_to_remove)
                PARTICIPANT_DELETED.send(sender=self,
                                         matter=self.matter,
                                         participant=user_to_remove,
                                         user=self.removing_user)
            else:
                logger.error(u'User %s tried to remove the participant: %s in the matter: %s but were not the primary lawyer' %
                             (self.current_user, user_to_remove, self.matter))
                raise PermissionDenied('You are not allowed to remove a participant of this matter')
        else:
            logger.error(u'User %s is not the participating in matter : %s' % (user_to_remove, self.matter))
            raise PermissionDenied('This user is not a participant of this matter')
