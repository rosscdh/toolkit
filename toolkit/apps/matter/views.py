# -*- coding: utf-8 -*-
from django.core import signing
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView
from toolkit.apps.matter.signals import USER_DOWNLOADED_EXPORTED_MATTER

from toolkit.core import _managed_S3BotoStorage

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.matter.services import (MatterRemovalService, MatterParticipantRemovalService)
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.matter.services import MatterExportService
from toolkit.mixins import AjaxModelFormView, ModalView

from rest_framework.renderers import UnicodeJSONRenderer

from . import MATTER_EXPORT_DAYS_VALID
from .forms import MatterForm

import datetime
import dateutil
import logging
logger = logging.getLogger('django.request')


class MatterDownloadExportView(DetailView):
    model = Workspace

    def dispatch(self, request, *args, **kwargs):
        #
        # take the passed in token and decode it, use the decoded parameters
        # to try to find and serve the exported zip file from s3
        #
        self.storage = _managed_S3BotoStorage()
        self.export_service = None

        token_data = signing.loads(kwargs.get('token'), salt=settings.SECRET_KEY)

        kwargs.update(token_data)
        kwargs.update({'slug': token_data.get('matter_slug')})
        self.kwargs = kwargs

        return super(MatterDownloadExportView, self).dispatch(request, *args, **kwargs)

    def has_not_expired(self, created_at):
        return created_at + datetime.timedelta(days=MATTER_EXPORT_DAYS_VALID) > datetime.datetime.today()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.export_service = MatterExportService(matter=self.object, requested_by=request.user)

        created_at = dateutil.parser.parse(kwargs.get('created_at'))

        if request.user.pk != kwargs.get('user_pk'):
            #
            # user_id does not match, only matter.lawyer can download atm
            #
            logger.critical("%s tried accessing %s (%s) but is not allowed." % (request.user, self.object, created_at))
            return HttpResponseForbidden('You are not allowed to access this file.')

        if self.has_not_expired(created_at=created_at):

            # get the name of the zip file on the s3 storage device
            zip_filename = self.export_service.get_zip_filename(kwargs)

            if not self.storage.exists(zip_filename):
                #
                # File was not found
                #
                return HttpResponseNotFound('%s was not found on s3' % zip_filename)

            else:
                response = HttpResponse()
                response['Content-Disposition'] = 'attachment; filename=%s_%s.zip' % \
                                                  (kwargs.get('matter_slug'), created_at.strftime('%Y-%m-%d_%H-%M-%S'))
                response['Content-Type'] = 'application/zip'

                #
                # Open the file on s3 and write its contents out to the response
                #
                with self.storage.open(zip_filename, 'r') as exported_zipfile:
                    response.write(exported_zipfile.read())
                #
                # Record this event
                #
                USER_DOWNLOADED_EXPORTED_MATTER.send(sender=self, matter=self.object, user=request.user)

                return response

        logger.info("%s tried accessing %s (%s) but his link had expired." % (request.user, self.object, created_at))
        return HttpResponseForbidden('Your download link has expired.')


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matter/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        object_list = self.get_serializer(self.object_list, many=True).data

        context.update({
            'can_create': True,
            'can_delete': True,
            'can_edit': True,
            #'object_list': self.object_list,
            'object_list_json': UnicodeJSONRenderer().render(object_list),
        })

        return context

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.serializer_class
        self.get_serializer_context()
        return serializer_class(instance)

    def get_serializer_context(self):
        return {
            'request': self.request
        }


class MatterDetailView(DetailView):
    """
    Just a proxy view through to the AngularJS app.
    """
    model = Workspace
    slug_url_kwarg = 'matter_slug'

    def get_template_names(self):
        if settings.PROJECT_ENVIRONMENT in ['prod'] or settings.DEBUG is False:
            return ['dist/index.html']
        else:
            return ['index.html']


class MatterCreateView(ModalView, AjaxModelFormView, CreateView):
    form_class = MatterForm

    @method_decorator(user_passes_test(lambda u: u.profile.validated_email is True, login_url=reverse_lazy('me:email-not-validated')))
    def dispatch(self, *args, **kwargs):
        return super(MatterCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(MatterCreateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'is_new': True
        })
        return kwargs

    def get_success_url(self):
        return self.object.get_absolute_url()


class MatterUpdateView(ModalView, AjaxModelFormView, UpdateView):
    form_class = MatterForm
    model = Workspace
    slug_url_kwarg = 'matter_slug'

    def get_form_kwargs(self):
        kwargs = super(MatterUpdateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'is_new': False
        })
        return kwargs

    def get_success_url(self):
        return reverse('matter:list')


class MatterDeleteView(ModalView, DeleteView):
    model = Workspace
    slug_url_kwarg = 'matter_slug'
    template_name = 'matter/matter_confirm_delete.html'

    def get_success_url(self):
        return reverse('matter:list')

    def get_context_data(self, **kwargs):
        context = super(MatterDeleteView, self).get_context_data(**kwargs)
        context.update({
            'action': 'delete' if self.request.user == self.object.lawyer else 'stop-participating'
        })
        return context

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()

        if self.object.lawyer == request.user:
            service = MatterRemovalService(matter=self.object, removing_user=request.user)
            service.process()

        else:
            #
            # Is a participant trying to stop participating
            #
            service = MatterParticipantRemovalService(matter=self.object, removing_user=request.user)
            service.process(user_to_remove=request.user)

        return HttpResponseRedirect(success_url)
