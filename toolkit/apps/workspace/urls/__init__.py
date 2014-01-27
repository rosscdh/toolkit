# -*- coding: utf-8 -*-
"""
Import the urls from the respective module files
and name them appropriately
then create the django std urlpatterns var and append our custom urls to it
"""
from .workspace import urlpatterns as workspace_urlpatterns
from .tool_objects import urlpatterns as tool_objects_urlpatterns

urlpatterns = workspace_urlpatterns
urlpatterns += tool_objects_urlpatterns