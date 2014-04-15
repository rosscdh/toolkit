# -*- coding: utf-8 -*-
from toolkit.apps.workspace.models import Workspace
from django.core.exceptions import PermissionDenied

import datetime
import logging
logger = logging.getLogger('django.request')


class MatterCloneService(object):
    """
    Service to clone a matter as a new matter
    """
    source_matter = None
    target_matter = None

    def __init__(self, source_matter, target_matter):
        self.source_matter = source_matter
        self.target_matter = target_matter

        assert type(self.source_matter) == Workspace, 'source_matter must be a Workspace type'
        assert self.source_matter.pk not in [None, ''], 'source_matter must have a pk'

        assert type(self.target_matter) == Workspace, 'target_matter must be a Workspace type'
        assert self.target_matter.pk not in [None, ''], 'target_matter must have a pk'

    def process(self):
        num_items = self.source_matter.item_set.all().count()

        logger.info('Cloning Matter source: %s target: %s num_items: %d' % (self.source_matter, self.target_matter, num_items) )

        for item in self.source_matter.item_set.all():

            item.pk = None  # pk should be regenerated
            item.slug = None  # slug must be unique too
            item.matter = self.target_matter  # set the matter to be the target matter
            item.latest_revision = None  # remove any connected revisions
            item.save()  # save it out

        self.target_matter.data['cloned'] = {
            'date_cloned': datetime.datetime.utcnow(),
            'num_items': num_items,
        }
        self.target_matter.save(update_fields=['data'])


class MatterRemovalService(object):
    """
    Service to delete the whole matter or to remove a participant from the matter
    """
    matter = None
    current_user = None

    def __init__(self, matter, current_user):
        self.matter = matter
        self.current_user = current_user

    def deleteMatter(self):
        if self.current_user == self.matter.lawyer:
            #
            # Only the primary lawyer can delete the matter
            #
            self.matter.delete()
        else:
            logger.error('User %s tried to delete a matter: %s but was not the lawyer' % (self.current_user, self.matter))
            raise PermissionDenied('You are not a lawyer of this matter')

    def removeParticipant(self, participant):
        if participant in self.matter.participants.all():
            #
            # all participants can remove themselves; laywers can remove other participants but not the primary lawyer
            #
            if participant == self.matter.lawyer:
                logger.error('User %s tried to remove the primary lawyer in matter: %s' % (self.current_user, self.matter))
                raise PermissionDenied('You are not able to remove the primary lawyer')

            elif self.current_user.username == participant.username:
                self.matter.participants.remove(participant)
                self.matter.actions.user_stopped_participating(user=participant)

            elif self.current_user.is_lawyer:
                self.matter.participants.remove(participant)
                self.matter.actions.removed_matter_participant(matter=self.matter, removing_user=self.current_user, removed_user=participant)

            else:
                logger.error('User %s tried to remove the participant: %s in the matter: %s but was not a lawyer' % (self.current_user, participant, self.matter))
                raise PermissionDenied('You are not allowed to remove a participant of this matter')
        else:
            logger.error('Participant %s is not a participant of the matter: %s' % (participant, self.matter))
            raise PermissionDenied('This user is not a participant of this matter')
