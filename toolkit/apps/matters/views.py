from django.conf import settings
from django.views.generic import ListView, TemplateView

from toolkit.api.serializers import LiteMatterSerializer
from toolkit.apps.workspace.models import Workspace


class MatterListView(ListView):
    serializer_class = LiteMatterSerializer
    template_name = 'matters/matter_list.html'

    def get_queryset(self):
        return Workspace.objects.mine(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MatterListView, self).get_context_data(**kwargs)

        context.update({
            'object_list': self.get_serializer(self.object_list, many=True).data,
        })

        return context

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.serializer_class
        context = self.get_serializer_context()
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
        if settings.DEBUG:
            return 'index.html'
        else:
            return 'dist/index.html'
