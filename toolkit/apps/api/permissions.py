# -*- coding: utf-8 -*-
from rest_framework import permissions


class ApiObjectPermission(permissions.IsAuthenticated):
    """
    Hook out read,edit,delete up to the django-rulez helper
    methods
    """
    permission_granted = False

    def __init__(self, *args, **kwargs):
        self.permission_granted = False
        super(ApiObjectPermission, self).__init__(*args, **kwargs)

    def has_permission(self, request, view):
        """
        For these list views we need to pass the view object in
        and if that view object has the django-rulez methods attached
        then they will be applied
        """
        self.permission_granted = super(ApiObjectPermission, self).has_permission(request=request, view=view)
        #
        # allow for local override of base inherited permissions
        #
        if self.permission_granted is True:
            if request.method in ['POST', 'PUT', 'PATCH']:
                self.permission_granted = self.can_edit(request=request, view=view, obj=view)

            elif request.method in ['DELETE']:
                self.permission_granted = self.can_delete(request=request, view=view, obj=view)

            elif request.method in ['GET']:
                self.permission_granted = self.can_read(request=request, view=view, obj=view)

        return self.permission_granted

    def has_object_permission(self, request, view, obj):
        self.permission_granted = super(ApiObjectPermission, self).has_object_permission(request=request, view=view, obj=obj)
        #
        # allow for local override of base inherited permissions
        #
        if self.permission_granted is True:
            if request.method in ['POST', 'PUT', 'PATCH']:
                self.permission_granted = self.can_edit(request=request, view=view, obj=obj)

            elif request.method in ['DELETE']:
                self.permission_granted = self.can_delete(request=request, view=view, obj=obj)

            elif request.method in ['GET']:
                self.permission_granted = self.can_read(request=request, view=view, obj=obj)

        return self.permission_granted

    def can_edit(self, request, view, obj):
        if hasattr(obj, 'can_edit'):
            return obj.can_edit(user=request.user)
        return False

    def can_delete(self, request, view, obj):
        if hasattr(obj, 'can_delete'):
            return obj.can_delete(user=request.user)
        return False

    def can_read(self, request, view, obj):
        if hasattr(obj, 'can_read'):
            return obj.can_read(user=request.user)
        return False