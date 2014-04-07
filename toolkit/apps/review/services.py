# -*- coding: utf-8 -*-
from dj_crocodoc.services import CrocoDocConnectService


class CrocodocLoaderService(object):
    """
    Class to provide kwargs used to populate html template with params
    also used to provide url
    """
    user = None
    reviewdocument = None
    service = None

    def __init__(self, user, reviewdocument):
        self.user = user
        self.reviewdocument = reviewdocument
        self.ensure_reviewer()
        self.service = CrocoDocConnectService(document_object=self.reviewdocument.document,
                       app_label='attachment',
                       field_name='executed_file',
                       upload_immediately=False,  # this is handled by the ensure_local_file method
                       # important for sandboxing the view to the specified reviewer
                       reviewer=self.reviewdocument.reviewer)

    def ensure_reviewer(self):
        if self.reviewdocument.reviewer is None:
            #
            # @BUG seems that the reviewer for some reason has not been assigned
            #
            self.reviewdocument.save()  # calling save causes the system to reevaluate the reviewers

    def ensure_local_file(self):
        #
        # if crocodoc.is_new is True:
        #
        # Ensure we have a local copy of this file so it can be sent
        #
        if self.reviewdocument.ensure_file():
            # so we have a file, now lets upload it
            self.service.generate()

    def process(self):
        # if this is a brand new file, we now need to ensure its available lcoally
        # and then if/when it is upload it to crocdoc
        self.ensure_local_file()

        # @TODO this should ideally be set in the service on init
        # and session automatically updated
        # https://crocodoc.com/docs/api/ for more info
        CROCDOC_PARAMS = {
                "user": {
                    "name": self.user.get_full_name(),
                    "id": self.user.pk
                },
                "sidebar": 'auto',
                "editable": self.reviewdocument.is_current, # allow comments only if the item is current
                "admin": False, # noone should be able to delete other comments
                "downloadable": True, # everyone should be able to download a copy
                "copyprotected": False, # should not have copyprotection
                "demo": False,
                #
                # We create a ReviewDocument object for each and every reviewer
                # for the matter.participants there is 1 ReviewDocument object
                # that they all can see
                #
                #"filter": self.get_filter_ids() # must be a comma seperated list
        }
        #
        # Set out session key based on params above
        #
        self.service.obj.crocodoc_service.session_key(**CROCDOC_PARAMS),

        return {
            'crocodoc': self.service.obj.crocodoc_service,
            'crocodoc_view_url': self.service.obj.crocodoc_service.view_url(**CROCDOC_PARAMS),  # this is where the view params must be sent in order to show toolbar etc
            'CROCDOC_PARAMS': CROCDOC_PARAMS, # for testing the values
        }