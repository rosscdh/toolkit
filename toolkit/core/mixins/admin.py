from django.contrib import admin


class IsDeletedModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model._default_manager.all_with_deleted()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
