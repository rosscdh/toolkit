from django.views.generic import ListView

from toolkit.core.item.models import Item


class RequestListView(ListView):
    template_name = 'request/request_list.html'

    def get_queryset(self):
        return Item.objects.my_requests(self.request.user)
