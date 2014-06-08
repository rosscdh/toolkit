# -*- coding: utf-8 -*-

class MatterParticipantPermissionMixin(object):
    """
    Helper mixin since adding manual through table for matter.participants to
    cater to permissions
    """
    @property
    def permissions_model(self):
        """
        Returns the participants.through table in this case `WorkspaceParticipants`
        Which we cant import normally due to cyclic import issues
        """
        return self.participants.through

    # --------------------------------------------------------------------------
    # @NOTE: add_participant and remove_participant were added to cater for the use
    # of a custom through model for particiapnts instead of the generic relation
    # nevessary for permissions
    #
    def add_participant(self, user, **kwargs):
        update_fields = []

        role = kwargs.get('role', None)  # default to thirdparty

        if role is not None:
            # if an invalid role is passed in then except
            if role not in self.permissions_model.ROLES.get_values():
                raise Exception('Role is not a valid value must be in: %s see WorkspaceParticipants.ROLES' % (WorkspaceParticipants.ROLES.get_values()))

        # Get the object
        perm, is_new = self.permissions_model.objects.get_or_create(user=user, workspace=self)

        if role is not None:
            perm.role = role
            update_fields.append('role')
        #
        # if role is None it will default to the WorkspaceParticipants.role default (currently .client)
        #

        if is_new:
            # only do this if new
            perm.is_matter_owner = False
            update_fields.append('is_matter_owner')

            if user == self.lawyer:
                perm.is_matter_owner = True
                perm.role = self.permissions_model.ROLES.owner
                update_fields.append('role')

        if update_fields:
            perm.save(update_fields=update_fields)

        return perm

    def remove_participant(self, user):
        return WorkspaceParticipants.objects.filter(user=user, workspace=self).delete()

    def participant_has_permission(self, user, **kwargs):
        """
        Shortcut method 
        """
        return user.matter_permissions(matter=self).has_permission(**kwargs)
    # --------------------------------------------------------------------------