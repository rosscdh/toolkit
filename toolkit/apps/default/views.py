# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, RedirectView, FormView

from .forms import SignUpForm, SignInForm


class AuthenticateUserMixin(object):
    def authenticate(self, form):
        user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is not None:
             if user.is_active:
                login(self.request, user)

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

    def form_valid(self, form):
        # user a valid form log them in
        self.authenticate(form=form)
        return super(StartView, self).form_valid(form)

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