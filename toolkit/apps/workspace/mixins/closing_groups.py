# -*- coding: utf-8 -*-
"""
Closing groups allows Matter.items to be grouped by a name that is relevant to
the lawyer. Only the lawyer sees these groups and they allow them to see a 
list of items that are outstanding in a closing group as well as perform other
functions on that group like; download, send for signing etc
"""

class InvalidClosingGroupValue(Exception):
    """
    If the dev tries to set the value to something that is not a list
    """
    msg = 'closing_groups must be of type list'


class ClosingGroupDoesNotExist(Exception):
    """
    Throw exception when the dev tries to remove a CG that does not exist
    """
    msg = 'The specified Closing Group name does not exist'


class ClosingGroupStillInUse(Exception):
    """
    A dev can only delete a closing_group if NONE of the matters.item_set are
    still making use of it.
    i.e. you have to set an item.closing_group = None and save the item
    BEFORE trying to delete the closing group
    """
    msg = 'There are still items using this closing group'


class ClosingGroupsMixin(object):
    """
    Mixin to allow getting and setting of closing_groups
    as well as adding to and removing from closing_groups
    """
    @property
    def closing_groups(self):
        """
        Get the set of closing groups
        """
        return self.data.get('closing_groups', [])

    @closing_groups.setter
    def closing_groups(self, value):
        """
        Set the closing group value
        """
        if type(value) == list:
            self.data['closing_groups'] = value
        else:
            raise InvalidClosingGroupValue

    def add_closing_group(self, value):
        """
        Add a new value to the closing_groups set
        """
        value = value.strip() if type(value) in [str, unicode] else value
        closing_groups = self.closing_groups

        if value not in ['', None]:
            if value not in closing_groups:
                # append the value
                closing_groups.append(value)
                # and then set our groups to the new list
                self.closing_groups = closing_groups
            return self.closing_groups
        return False

    def delete_closing_group(self, value):
        """
        Alias
        """
        return self.remove_closing_group(value=value)

    def remove_closing_group(self, value, instance=None):
        """
        Remove an existing value from the set
        but only if there are no items that have that value
        """
        value = value.strip() if type(value) in [str, unicode] else value
        closing_groups = self.closing_groups

        if value not in ['', None]:
            if value not in closing_groups:
                #
                # did not find this value in the set
                #
                raise ClosingGroupDoesNotExist

            else:
                #
                # Now check to see if any other items are still using it
                #
                instance_pk = instance.pk if instance is not None else None
                # exclude the instance if present
                num_items_using_closing_group = self.item_set  \
                                                    .exclude(pk=instance_pk) \
                                                    .filter(closing_group=value).count()

                if num_items_using_closing_group > 0:
                    #
                    # There are still items using this closing_group
                    #
                    raise ClosingGroupStillInUse

                else:
                    # remove it
                    closing_groups.remove(value)
                    # update the set
                    self.closing_groups = closing_groups
                return self.closing_groups
        return False
