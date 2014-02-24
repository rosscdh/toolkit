# -*- coding: utf-8 -*-
"""
Categories allows Matter.items to be grouped by a name that is relevant to
the lawyer. Only the lawyer sees these groups and they allow them to see a 
list of items that are outstanding in a closing group as well as perform other
functions on that group like; download, send for signing etc
"""

class InvalidCategoryValue(Exception):
    """
    If the dev tries to set the value to something that is not a list
    """
    msg = 'categories must be of type list'


class CategoryDoesNotExist(Exception):
    """
    Throw exception when the dev tries to remove a CG that does not exist
    """
    msg = 'The specified category name does not exist'


class CategoryStillInUse(Exception):
    """
    A dev can only delete a category if NONE of the matters.item_set are
    still making use of it.
    i.e. you have to set an item.category = None and save the item
    BEFORE trying to delete the closing group
    """
    msg = 'There are still items using this category'


class CategoriesMixin(object):
    """
    Mixin to allow getting and setting of categories
    as well as adding to and removing from categories
    """
    @property
    def categories(self):
        """
        Get the set of closing groups
        """
        return self.data.get('categories', [])

    @categories.setter
    def categories(self, value):
        """
        Set the closing group value
        """
        if type(value) != list:
            raise InvalidCategoryValue
        self.data['categories'] = value

    def add_category(self, value):
        """
        Add a new value to the categories set
        """
        categories = self.categories

        if value not in categories:
            # append the value
            categories.append(value)
            # and then set our groups to the new list
            self.categories = categories

    def delete_category(self, value):
        """
        Alias
        """
        self.remove_category(value=value)

    def remove_category(self, value):
        """
        Remove an existing value from the set
        but only if there are no items that have that value
        """
        categories = self.categories

        if value not in categories:
            #
            # did not find this value in the set
            #
            raise CategoryDoesNotExist

        else:
            #
            # Now check to see if any other items are still using it
            #
            num_items_using_category = self.item_set.filter(category=value).count()

            if num_items_using_category > 0:
                #
                # There are still items using this category
                #
                raise CategoryStillInUse

            else:
                # remove it
                categories.remove(value)
                # update the set
                self.categories = categories
