# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, RedirectView, FormView

from .forms import SignUpForm, SignInForm, InviteKeyForm

import logging
LOGGER = logging.getLogger('django.request')


class UserInactiveException(Exception):
    message = 'User is not active'


class UserNotFoundException(Exception):
    message = 'User could not be authenticated'


class AuthenticateUserMixin(object):
    def get_auth(self, form):
        return authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])

    def authenticate(self, form):
        user = self.get_auth(form=form)
        if user is not None:
            LOGGER.info('user is authenticated: %s' % user)
            if user.is_active:
                LOGGER.info('user is active: %s' % user)
                login(self.request, user)
            else:
                LOGGER.info('user is not active: %s' % user)
                raise UserInactiveException
        else:
            LOGGER.info('User not authenticated')
            raise UserNotFoundException

class LogOutMixin(object):
    """
    Mixin that will log the current user out
    and continue showing the view as an non authenticated user
    """
    def dispatch(self, request, *args, **kwargs):
        """
        If the user is logged in log them out
        """
        if request.user.is_authenticated() is True:
            logout(request)

        return super(LogOutMixin, self).dispatch(request, *args, **kwargs)


class SaveNextUrlInSessionMixin(object):
    """
    A mixin that will save a ?next=/path/to/next/page
    url in the session
    """
    def get(self, request, *args, **kwargs):
        next = request.GET.get('next', None)

        if next is not None:
            self.request.session['next'] = next

        return super(SaveNextUrlInSessionMixin, self).get(request, *args, **kwargs)


class StartView(LogOutMixin, SaveNextUrlInSessionMixin, AuthenticateUserMixin, FormView):
    """
    sign in view
    """
    template_name = 'public/start.html'
    form_class = SignInForm

    def get_success_url(self):
        return reverse('dash:default')

    def form_valid(self, form):
        # user a valid form log them in
        try:
            LOGGER.info('authenticating user: %s' % form.cleaned_data.get('email'))
            self.authenticate(form=form)

        except UserNotFoundException, UserInactiveException:
            return self.form_invalid(form=form)

        return super(StartView, self).form_valid(form)


class InviteKeySignInView(StartView):
    form_class = InviteKeyForm

    def get_auth(self, form):
        return authenticate(username=form.cleaned_data.get('invite_key'), password=None)


class SignUpView(LogOutMixin, FormView):
    """
    signup view
    """
    template_name = 'public/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        # user a valid form log them in
        return super(StartView, self).form_valid(form)


class LogoutView(LogOutMixin, RedirectView):
    """
    The logout view
    """
    url = '/'
