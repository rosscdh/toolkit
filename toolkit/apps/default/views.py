# -*- coding: utf-8 -*-
import urllib

from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic import TemplateView, RedirectView, FormView

from .forms import SignUpForm, SignInForm, VerifyTwoFactorForm

from toolkit.apps.workspace.forms import InviteKeyForm
from toolkit.apps.workspace.models import InviteKey
from toolkit.apps.me.mailers import ValidateEmailMailer

from toolkit.core.services.analytics import AtticusFinch

import logging
logger = logging.getLogger('django.request')


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
            logger.info('user is authenticated: %s' % user)

            if user.is_active:
                logger.info('user is active: %s' % user)
                login(self.request, user)
            else:
                logger.info('user is not active: %s' % user)
                raise UserInactiveException
        else:
            logger.info('User not authenticated')
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


class StartView(LogOutMixin, SaveNextUrlInSessionMixin, AuthenticateUserMixin, FormView):
    """
    sign in view
    """
    authenticated_user = None
    form_class = SignInForm
    template_name = 'public/start.html'

    def get_success_url(self):
        url = reverse('matter:list')

        if self.authenticated_user.profile.data.get('two_factor_enabled', False):
            url = reverse('public:signin-two-factor')
        else:
            next = self.request.session.get('next')
            if next is not None:
                url = next

        return url

    def form_invalid(self, form):
        analytics = AtticusFinch()
        ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
        analytics.anon_event('user.login.invalid', distinct_id=form.data.get('email'), ip_address=ip_address)
        return super(StartView, self).form_invalid(form=form)

    def form_valid(self, form):
        # user a valid form log them in
        try:

            logger.info('authenticating user: %s' % form.cleaned_data.get('email'))
            self.authenticated_user = self.get_auth(form=form)

        except (UserNotFoundException, UserInactiveException):

            return self.form_invalid(form=form)

        if self.authenticated_user.profile.data.get('two_factor_enabled', False):
            self.request.session['user'] = self.authenticated_user.username
        else:
            self.login(user=self.authenticated_user)

            analytics = AtticusFinch()

            ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
            analytics.event('user.login', user=self.authenticated_user, ip_address=ip_address)

            logger.info('Signed-up IP_ADDRESS List: %s' % ip_address)

        return super(StartView, self).form_valid(form)


class VerifyTwoFactorView(AuthenticateUserMixin, FormView):
    form_class = VerifyTwoFactorForm
    template_name = 'public/verify_two_factor.html'

    def get(self, request, *args, **kwargs):
        self.authenticated_user = self.get_user()
        return super(VerifyTwoFactorView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.authenticated_user = self.get_user()
        return super(VerifyTwoFactorView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(VerifyTwoFactorView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'user': self.authenticated_user,
        })
        return kwargs

    def get_user(self):
        try:
            user = User.objects.get(username=self.request.session['user'])
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            return user
        except KeyError:
            raise Http404('No user found in the session')

    def form_valid(self, form):
        try:
            self.login(user=self.authenticated_user)

        except (UserNotFoundException, UserInactiveException):
            return self.form_invalid(form=form)

        analytics = AtticusFinch()

        ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
        analytics.event('user.login', user=self.authenticated_user, ip_address=ip_address)

        logger.info('Logged-in IP_ADDRESS: %s' % ip_address)

        return super(VerifyTwoFactorView, self).form_valid(form)

    def get_success_url(self):
        url = reverse('matter:list')

        next = self.request.session.get('next')
        if next is not None:
            url = next

        return url


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

    def get_auth(self, form=None, invite_key=None):
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
        return reverse('matter:list') + '?' + urllib.urlencode({
            'firstseen': 1
        })

    def form_valid(self, form):
        # user a valid form log them in

        form.save()  # save the user
        self.authenticate(form=form)  # log them in

        mailer = ValidateEmailMailer(((self.request.user.get_full_name(), self.request.user.email,),))
        mailer.process(user=self.request.user)

        messages.info(self.request, 'Your account has been created. Please verify your email address. Check your email and click on the link that we\'ve sent you.')

        analytics = AtticusFinch()
        analytics.event('user.signup', user=self.request.user, ip_address=self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR')))

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


class LoginErrorView(TemplateView):
    template_name = 'public/login_error.html'