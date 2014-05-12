from StringIO import StringIO
import datetime
import dateutil
from django.conf import settings
from django.core import signing
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView, DetailView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from toolkit.core import _managed_S3BotoStorage

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.matter.services import (MatterRemovalService, MatterParticipantRemovalService)
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.matter.services import MatterExportService
from toolkit.mixins import AjaxModelFormView, ModalView

from rest_framework.renderers import UnicodeJSONRenderer

from .forms import MatterForm

import logging
logger = logging.getLogger('django.request')


MATTER_EXPORT_DAYS_VALID = getattr(settings, 'MATTER_EXPORT_DAYS_VALID', 3)


class MatterDownloadExportView(DetailView):
    model = Workspace

    def dispatch(self, request, *args, **kwargs):
        token_data = signing.loads(kwargs.get('token'), salt=settings.SECRET_KEY)
        kwargs.update(token_data)
        kwargs.update({'slug': token_data.get('matter_slug')})
        self.kwargs = kwargs
        return super(MatterDownloadExportView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        created_at = dateutil.parser.parse(kwargs.get('created_at'))

        if request.user.pk != kwargs.get('user_pk'):
            logger.critical("%s tried accessing %s (%s) but is not allowed." % (request.user, self.object, created_at))
            return HttpResponseForbidden('You are not allowed to access this file.')

        if created_at and created_at + datetime.timedelta(days=MATTER_EXPORT_DAYS_VALID) > datetime.datetime.now():
            zip_filename = MatterExportService(self.object).get_zip_filename(kwargs)
            if _managed_S3BotoStorage().exists(zip_filename):
                response = HttpResponse()
                response['Content-Disposition'] = 'attachment; filename=%s_%s.zip' % \
                                                  (kwargs.get('matter_slug'), created_at.strftime('%Y-%m-%d_%H-%M-%S'))
                response['Content-Type'] = 'application/zip'
                s3_storage = _managed_S3BotoStorage()
                with s3_storage.open(zip_filename, 'r') as myfile:
                    response.write(myfile.read())
                self.object.actions.user_downloaded_exported_matter(user=self.object.lawyer)
                return response
            else:
                logger.critical('Exported matter should be in S3 but is not: %s' % zip_filename)

        logger.critical("%s tried accessing %s (%s) but his link had expired." % (request.user, self.object, created_at))
        return HttpResponseForbidden('Your link has expired.')


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matter/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        object_list = self.get_serializer(self.object_list, many=True).data

        context.update({
            'can_create': self.request.user.profile.is_lawyer,
            'can_delete': self.request.user.profile.is_lawyer,
            'can_edit': self.request.user.profile.is_lawyer,
            #'object_list': object_list,
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


class MatterDetailView(TemplateView):
    """
    Just a proxy view through to the AngularJS app.
    """
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
