# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, RedirectView, FormView

from .forms import SignUpForm, SignInForm

from toolkit.apps.workspace.forms import InviteKeyForm
from toolkit.apps.workspace.models import Workspace, InviteKey

import logging
LOGGER = logging.getLogger('django.request')


def handler500(request, *args, **kwargs):
    """
    Override for the 500 response so that we have access to the STATIC_URL and MEDIA_URL
    handler500 = 'glynt.apps.default.views.handler500'
    """
    return render(request, template_name='500.html', status=500)


class UserInactiveException(Exception):
    message = 'User is not active'


class UserNotFoundException(Exception):
    message = 'User could not be authenticated'


class AuthenticateUserMixin(object):
    def get_auth(self, form):
        return authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])

    def authenticate(self, form):
        user = self.get_auth(form=form)
        self.login(user=user)

    def login(self, user=None):
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
        self.save_next_in_session(next=next)
        return super(SaveNextUrlInSessionMixin, self).get(request, *args, **kwargs)

    def save_next_in_session(self, next=None):
        if next is not None:
            self.request.session['next'] = next


class RedirectToNextMixin(object):
    def redirect(self, next=None):
        return HttpResponseRedirect(next) if next is not None else next


class StartView(LogOutMixin, SaveNextUrlInSessionMixin, AuthenticateUserMixin, FormView):
    """
    sign in view
    """
    template_name = 'public/start.html'
    form_class = SignInForm

    def get_success_url(self):
        url = reverse('matter:list')
        tool_redirect_url = None
        if self.request.user.profile.is_customer is True:
            #
            # Redirect the user to the current invite workspace
            #
            invite_key = InviteKey.objects.filter(invited_user=self.request.user).first()
            if invite_key is not None:
                tool_redirect_url = invite_key.get_tool_instance_absolute_url()

        return url if tool_redirect_url is None else tool_redirect_url

    def form_valid(self, form):
        # user a valid form log them in
        try:
            LOGGER.info('authenticating user: %s' % form.cleaned_data.get('email'))
            self.authenticate(form=form)

        except UserNotFoundException, UserInactiveException:
            return self.form_invalid(form=form)

        return super(StartView, self).form_valid(form)


class HomePageView(StartView):
    # now inherits from startview
    #template_name = 'public/home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('matter:list'))
        else:
            return super(HomePageView, self).dispatch(request, *args, **kwargs)


class InviteKeySignInView(StartView):
    form_class = InviteKeyForm

    def dispatch(self, request, *args, **kwargs):
        """
        If we have a key in the url
        """
        response = None
        if request.user.is_authenticated() is True:
            logout(request)

        if 'key' in kwargs and kwargs.get('key', None) is not None:
            response = self.login_via_key(key=kwargs.get('key'))

        if response is not None:
            return response
        else:
            return super(InviteKeySignInView, self).dispatch(request, *args, **kwargs)

    def login_via_key(self, key=None):
        if key is not None:
            invite = InviteKey.objects.get(key=key)

            # set the next in the session
            # this is due to the EnsureUserHasPasswordMiddleware
            # which redirects to password if they have not set it
            #self.request.session['next'] = next

            user = self.get_auth(invite_key=key)
            self.login(user=user)

            if self.request.user.is_authenticated() is True:
                return HttpResponseRedirect(invite.next)
        return None

    def get_auth(self, form=None,  invite_key=None):
        if invite_key is not None:
            return authenticate(username=invite_key, password=None)

        if form is not None:
            return authenticate(username=form.cleaned_data.get('invite_key'), password=None)

        return None


class SignUpView(LogOutMixin, AuthenticateUserMixin, FormView):
    """
    signup view
    """
    template_name = 'public/signup.html'
    form_class = SignUpForm

    def get_success_url(self):
        return reverse('matter:list')

    def form_valid(self, form):
        # user a valid form log them in

        form.save()  # save the user
        self.authenticate(form=form)  # log them in

        return super(SignUpView, self).form_valid(form)


class LogoutView(LogOutMixin, RedirectView):
    """
    The logout view
    """
    url = '/'


class DisclaimerView(TemplateView):
    template_name = 'legal/disclaimer.html'


class PrivacyView(TemplateView):
    template_name = 'legal/privacy.html'


class TermsView(TemplateView):
    template_name = 'legal/terms.html'
