# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ObjectDoesNotExist

from .mixins import EmailIsValidatedMixin
from .managers import CustomUserManager

from jsonfield import JSONField
from sorl.thumbnail.images import ImageFile

import logging
logger = logging.getLogger('django.request')


class UserProfile(EmailIsValidatedMixin, models.Model):
    """
    Base User Profile, where we store all the interesting information about
    users
    """
    CUSTOMER = 'customer'
    LAWYER = 'lawyer'

    has_notifications = models.BooleanField(default=False)

    user = models.OneToOneField('auth.User',
                                unique=True,
                                related_name='profile')

    data = JSONField(default={"user_class": "customer"})

    @classmethod
    def create(cls, **kwargs):
        profile = cls(**kwargs)
        profile.save()
        return profile

    def __getattr__(self, key):
        try:
            # if key is of invalid type or value, the list values
            # will raise the error
            return self.data[key]
        except KeyError:
            raise AttributeError

    def __unicode__(self):
        return '%s <%s>' % (self.user.get_full_name(), self.user.email)

    @property
    def user_class(self):
        return self.data.get('user_class', None)

    @user_class.setter
    def user_class(self, value):
        if value in [self.CUSTOMER, self.LAWYER]:
            self.data['user_class'] = value

    @property
    def is_lawyer(self):
        return self.user_class == self.LAWYER

    @property
    def is_customer(self):
        return self.user_class == self.CUSTOMER

    @property
    def account_type(self):
        return 'Paid' if self.subscription else 'Free'
        # return 'Complimentary'

    @property
    def plan(self):
        if self.subscription:
            plan, interval = self.subscription.plan.rsplit('-', 1)
            return plan
        return 'trial'

    @property
    def plan_interval(self):
        if self.subscription:
            plan, interval = self.subscription.plan.rsplit('-', 1)
            return interval

    @property
    def subscription(self):
        try:
            return self.user.customer.current_subscription
        except ObjectDoesNotExist:
            pass

    @property
    def type(self):
        return 'Attorney' if self.is_lawyer else 'Client'

    @property
    def firm_name(self):
        return self.data.get('firm_name', None)

    @property
    def firm_logo(self):
        firm_logo = self.data.get('firm_logo', None)
        if firm_logo is not None:
            return ImageFile(firm_logo)
        return firm_logo

    @property
    def matters_created(self):
        return self.data.get('matters_created', 0)

    @matters_created.setter
    def matters_created(self, value):
        if type(value) in [int]:
            self.data['matters_created'] = value

    @property
    def verified(self):
        return self.data.get('validated_email', False)


def _get_or_create_user_profile(user):
    # set the profile
    # This is what triggers the whole cleint profile creation process in pipeline.py:ensure_user_setup
    try:
        profile, is_new = UserProfile.objects.get_or_create(user=user)  # added like this so django noobs can see the result of get_or_create
        return (profile, is_new,)

    except Exception as e:
        logger.critical('transaction.atomic() integrity error: %s' % e)

    return (None, None,)


# used to trigger profile creation by accidental refernce. Rather use the _create_user_profile def above
User.profile = property(lambda u: _get_or_create_user_profile(user=u)[0])
User.add_to_class('objects', CustomUserManager())


"""
Overide the user __unicode__ method to actually return somethign useful.

"""
def custom__unicode__(self, **kwargs):
    name = '%s %s' % (self.first_name, self.last_name)
    if name.strip() in ['', None]:
        name = self.email
    return name

User.add_to_class('__unicode__', custom__unicode__)

"""
Overide the user get_full_name method to actually return somethign useful if
there is no name.

Used to return the email address as their name, if no first/last name exist.
"""
def get_full_name(self, **kwargs):
    name = '%s %s' % (self.first_name, self.last_name)
    if name.strip() in ['', None]:
        name = self.email
    return name

User.add_to_class('get_full_name', get_full_name)

"""
Add in the get_initials method, which returns the user initials based on their
first and last name
"""
def get_initials(self):
    initials = None
    try:
        initials = '%s%s' % (self.first_name[0], self.last_name[0])
        initials = initials.strip().upper()
    except IndexError:
        pass

    if initials in ['', None]:
        return None
    return initials

User.add_to_class('get_initials', get_initials)

"""
Permissions: Get or create a permissions object for this user
"""
def get_matter_permissions(self, matter):
    if self in matter.participants.all():
        permission, is_new = self.workspaceparticipants_set.get_or_create(user=self, workspace=matter)
        return permission
    return self.workspaceparticipants_set.model(user=self, workspace=matter)

User.add_to_class('matter_permissions', get_matter_permissions)


"""
Add our api permission handler methods to the User class
"""
def user_can_read(self, **kwargs):
    return True

def user_can_edit(self, **kwargs):
    return False

def user_can_delete(self, **kwargs):
    return False

User.add_to_class('can_read', user_can_read)
User.add_to_class('can_edit', user_can_edit)
User.add_to_class('can_delete', user_can_delete)

"""
Upgrade the Permission class .name to be longer
"""
Permission._meta.get_field('name').max_length = 128
