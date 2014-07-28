from django.contrib import admin

from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    actions = ['resync_counts']

    def resync_counts(self, request, queryset):
        from toolkit.core.item.models import Item

        # queryset.update(status='p')
        for profile in queryset.all():
            profile.data['open_requests'] = Item.objects.my_requests(profile.user).get('count', 0)
            profile.save(update_fields=['data'])
    resync_counts.short_description = "Re-sync selected user counts"

admin.site.register(UserProfile, UserProfileAdmin)
