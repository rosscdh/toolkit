from django.views.generic import ListView

from toolkit.core.item.models import Item


class CompletedRequestListView(ListView):
    template_name = 'request/request_list.html'

    def get_context_data(self, **kwargs):
        context = super(CompletedRequestListView, self).get_context_data(**kwargs)
        context.update({ 'show_completed': True })
        return context

    def get_queryset(self):
        return Item.objects.my_requests(self.request.user, completed=True)


class OpenRequestListView(ListView):
    template_name = 'request/request_list.html'

    def get_context_data(self, **kwargs):
        context = super(OpenRequestListView, self).get_context_data(**kwargs)
        context.update({ 'show_completed': False })
        return context

    def get_queryset(self):
        return Item.objects.my_requests(self.request.user)
