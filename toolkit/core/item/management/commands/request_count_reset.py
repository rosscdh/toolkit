# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from toolkit.apps.default.models import UserProfile
from toolkit.core.item.models import Item


class Command(BaseCommand):
    args = '<username>'
    help = "Reset the open_requests count value for each or a specific user by username"

    def get_profiles(self, *usernames):
        if usernames:
            return UserProfile.objects.select_related('user').filter(user__username__in=usernames)
        return UserProfile.objects.select_related('user').all()

    def handle(self, *args, **options):

        for profile in self.get_profiles(*args):
            count = Item.objects.my_requests(profile.user).get('count', 0)
            current_count = profile.data.get('open_requests', 0)

            if count != current_count:
                print('Updated User: %s count: %d current: %d' % (profile.user, count, current_count))

                profile.data['open_requests'] = count
                profile.save(update_fields=['data'])
            else:
                print('No Update for: %s count: %s' % (profile.user, count))