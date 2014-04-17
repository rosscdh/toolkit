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
    removing_user = None

    def __init__(self, matter=None, removing_user=None):
        self.matter = matter
        self.removing_user = removing_user

    def process(self, user_to_remove=None):
        if self.removing_user == user_to_remove and self.removing_user == self.matter.lawyer:
            #
            # Only the primary lawyer can delete the matter
            #
            self.matter.delete()
        elif user_to_remove in self.matter.participants.all():
            #
            # all participants can remove themselves; laywers can remove other participants but not the primary lawyer
            #
            if self.removing_user == user_to_remove:
                self.matter.participants.remove(user_to_remove)
                self.matter.actions.user_stopped_participating(user=user_to_remove)

            elif self.removing_user.profile.is_lawyer:
                self.matter.participants.remove(user_to_remove)
                self.matter.actions.removed_matter_participant(matter=self.matter, removing_user=self.removing_user, removed_user=user_to_remove)

            else:
                logger.error(u'User %s tried to remove the participant: %s in the matter: %s but was not a lawyer' % (self.current_user, user_to_remove, self.matter))
                raise PermissionDenied('You are not allowed to remove a participant of this matter')
        else:
            logger.error(u'User %s is not the primary lawyer of the matter : %s and/or the user to remove: %s is not in the matter' % (self.removing_user, self.matter, self.user_to_remove))
            raise PermissionDenied('This user is not a participant of this matter and/or you are not the primary lawyer')