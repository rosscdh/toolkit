from django.contrib import admin

from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    actions = ['resync_counts']

    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    def resync_counts(self, request, queryset):
        from toolkit.core.item.models import Item

        for profile in queryset.all():
            profile.data['open_requests'] = Item.objects.my_requests(profile.user).get('count', 0)
            profile.save(update_fields=['data'])
    resync_counts.short_description = "Re-sync selected user counts"


admin.site.register(UserProfile, UserProfileAdmin)
