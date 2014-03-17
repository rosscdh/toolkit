# -*- coding: UTF-8 -*-
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import (MatterSerializer, SimpleUserSerializer)
from .item import MatterItemView


class ItemRequestRevisionView(MatterItemView):
    """
    An item can be created that allows a request to be sent
    to the item.responsible_party user
    must also have a status of:
    (1, 'awaiting_document', 'Awaiting Document'),
    """
    http_method_names = ('get', 'patch',)

    note = None  # provided by requesting party and added to item.data json obj


    def get_serializer(self, instance, data=None,
                       files=None, many=False, partial=False):
        """
        Remove the note from the data to be validated but use it again in 
        pre_save add it to the data
        """
        #
        # Save the note for later
        #
        self.note = data.pop('note', None) if data is not None else None

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

    def pre_save(self, obj):
        obj.is_requested = True
        #
        # Cant use the generic note and requested_by setters due to atomic locks
        # raises TransactionManagementError
        #
        obj.data.update({
            'request_document': {
                'note': self.note,
                'requested_by': SimpleUserSerializer(self.request.user, context={'request': self.request}).data,
            }
        })

        obj.responsible_party = self.responsible_party(obj=obj)

        return super(ItemRequestRevisionView, self).pre_save(obj=obj)
