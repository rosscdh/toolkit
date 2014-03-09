# -*- coding: UTF-8 -*-
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import MatterSerializer
from .item import MatterItemsView


class ItemRequestRevisionView(MatterItemsView):
    """
    An item can be created that allows a request to be sent
    to the item.responsible_party user
    must also have a status of:
    (1, 'awaiting_document', 'Awaiting Document'),
    """
    note = None  # provided by requesting party and added to item.data json obj

    def get_queryset(self):
        """
        Filter the default set of items by status = awaiting_document
        """
        qs = super(ItemRequestRevisionView, self).get_queryset()
        return qs.filter(status=self.model.ITEM_STATUS.awaiting_document)

    def get_serializer(self, **kwargs):
        """
        Remove the note from the data to be validated but use it again in 
        pre_save add it to the data
        """
        data = kwargs.get('data', {})
        #
        # Save the note for later
        #
        self.note = data.pop('note', None)
        # add the item name if not present
        data.update({
            'matter': MatterSerializer(self.matter, context={'request': self.request}).data.get('url'),
            'name': kwargs.get('name', 'Requested a document'),
        })

        kwargs.update({'data': data})

        return super(ItemRequestRevisionView, self).get_serializer(**kwargs)

    def responsible_party(self, obj):
        service = EnsureCustomerService(username=username, full_name=None)
        is_new, user, profile = service.process()
        return is_new, user, profile

    def pre_save(self, obj):
        obj.status = obj.ITEM_STATUS.awaiting_document
        # get the data json object
        data = obj.data
        # get the request_document from within that
        request_document = data.get('request_document', {})
        request_document['note'] = self.note

        # update
        data['request_document'] = request_document
        obj.data = data

        #is_new, obj.responsible_party, profile = self.responsible_party(obj=obj)

        return super(ItemRequestRevisionView, self).pre_save(obj=obj)

    # def post_save(self, obj):
    #     #
    #     # Send email to the user
    #     #
    #     pass