# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework import routers

from toolkit.apps.eightythreeb.api import EightyThreeBViewSet
from toolkit.apps.workspace.api import InviteKeyViewSet

router = routers.DefaultRouter()


router.register(r'83b', EightyThreeBViewSet)
router.register(r'invite', InviteKeyViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
)