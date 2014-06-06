# -*- coding: UTF-8 -*-
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import (SimpleUserSerializer)
from .item import MatterItemView

import datetime

from rulez import registry as rulez_registry


class ItemRequestRevisionView(MatterItemView):
    """
    An item can be created that allows a request to be sent
    to the item.responsible_party user
    must also have a status of:
    (1, 'awaiting_document', 'Awaiting Document'),
    """
    http_method_names = ('get', 'patch',)

    message = None  # provided by requesting party and added to item.data json obj

    def get_serializer(self, instance, data=None,
                       files=None, many=False, partial=False):
        """
        Remove the note from the data to be validated but use it again in
        pre_save add it to the data
        """
        #
        # Save the note for later
        #
        self.message = data.pop('message', None) if data is not None else None

        return super(ItemRequestRevisionView, self).get_serializer(instance=instance,
                                                                   data=data,
                                                                   files=files,
                                                                   many=many,
                                                                   partial=partial)

    def responsible_party(self, obj):
        email = self.request.DATA.get('email')
        first_name = self.request.DATA.get('first_name')
        last_name = self.request.DATA.get('last_name')

        service = EnsureCustomerService(email=email, full_name='%s %s' % (first_name, last_name))
        is_new, user, profile = service.process()

        return user

    def pre_save(self, obj, **kwargs):
        obj.is_requested = True
        #
        # Cant use the generic note and requested_by setters due to atomic locks
        # raises TransactionManagementError
        #
        obj.data.update({
            'request_document': {
                'message': self.message,
                'requested_by': SimpleUserSerializer(self.request.user, context={'request': self.request}).data,
                'date_requested': datetime.datetime.utcnow()
            }
        })

        obj.responsible_party = self.responsible_party(obj=obj)

        return super(ItemRequestRevisionView, self).pre_save(obj=obj, **kwargs)

    def post_save(self, obj, **kwargs):
        """
        Send the email to the items responsible_party
        """
        self.object.send_document_requested_emails(from_user=self.request.user)

        # if is_requested is True the activity has to be created (similar to send_document_requested_emails())
        if self.object.is_requested is True:
            user = self.object.responsible_party
            if user:
                self.matter.actions.request_user_upload_revision(item=self.object,
                                                                 adding_user=self.request.user,
                                                                 added_user=user)

        super(ItemRequestRevisionView, self).post_save(obj=obj, **kwargs)

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user.has_perm('workspace.manage_requests', self.matter)

    def can_delete(self, user):
        return user.has_perm('workspace.manage_requests', self.matter)


rulez_registry.register("can_read", ItemRequestRevisionView)
rulez_registry.register("can_edit", ItemRequestRevisionView)
rulez_registry.register("can_delete", ItemRequestRevisionView)