# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from social.apps.django_app.utils import psa, STORAGE
from social.strategies.utils import get_strategy
from social.utils import user_is_authenticated
from social.apps.django_app.views import _do_login as social_auth_login
from social.exceptions import AuthException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (SocialAuthInputSerializer, UserSerializer,
    TokenSerializer, UserTokenSerializer)


REDIRECT_URI = getattr(settings, 'REST_SOCIAL_OAUTH_REDIRECT_URI', '/')


def load_strategy(request=None):
    return get_strategy('rest_social_auth.strategy.DRFStrategy', STORAGE, request)


@psa(REDIRECT_URI, load_strategy=load_strategy)
def register_by_auth_token(request, backend, *args, **kwargs):
    user = request.user
    redirect_uri = kwargs.pop('manual_redirect_uri', None)
    if redirect_uri:
        request.backend.redirect_uri = redirect_uri
    is_authenticated = user_is_authenticated(user)
    user = is_authenticated and user or None
    # skip checking state by setting following params to False
    # it is responsibility of front-end to check state
    # TODO: maybe create an additional resource, where front-end will
    # store the state before making a call to oauth provider
    # so server can save it in session and consequently check it before
    # sending request to acquire access token.
    # In case of token authentication we need a way to store an anonymous
    # session to do it.
    request.backend.REDIRECT_STATE = False
    request.backend.STATE_PARAMETER = False
    user = request.backend.complete(user=user, *args, **kwargs)
    return user


class BaseSocialAuthView(GenericAPIView):
    """
    View will login or signin (create) the user from social oauth2.0 provider.

    **Input** (default serializer_class_in):

        {
            "provider": "facebook",
            "code": "AQBPBBTjbdnehj51"
        }

    + optional

        "redirect_uri": "/relative/or/absolute/redirect/uri"

    **Output**:

    user data in serializer_class format
    """

    serializer_class_in = SocialAuthInputSerializer
    serializer_class = None

    def get_serializer_class_in(self):
        assert self.serializer_class_in is not None, (
            "'%s' should either include a `serializer_class_in` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.serializer_class_in

    def get_serializer_in(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class_in()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        serializer_in = self.get_serializer_in(data=request.data)
        serializer_in.is_valid(raise_exception=True)
        self.set_input_data(request, serializer_in.validated_data.copy())
        try:
            user = self.get_object()
        except AuthException as e:
            return self.respond_error(e)
        resp_data = self.get_serializer(instance=user)
        self.do_login(request.backend, user)
        return Response(resp_data.data)

    def get_object(self):
        provider = self.request.auth_data.pop('provider')
        manual_redirect_uri = self.request.auth_data.pop('redirect_uri', None)
        manual_redirect_uri = self.get_redirect_uri(manual_redirect_uri)
        return register_by_auth_token(self.request, provider,
            manual_redirect_uri=manual_redirect_uri)

    def do_login(self, backend, user):
        """
        Do login action here.
        For example in case of session authentication store the session in
        cookies.
        """

    def set_input_data(self, request, auth_data):
        """
        auth_data will be used used as request_data in strategy
        """
        request.auth_data = auth_data

    def get_redirect_uri(self, manual_redirect_uri):
        if not manual_redirect_uri:
            manual_redirect_uri = getattr(settings,
                'REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI', None)
        return manual_redirect_uri

    def respond_error(self, error):
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SocialSessionAuthView(BaseSocialAuthView):
    serializer_class = UserSerializer

    def do_login(self, backend, user):
        social_auth_login(backend, user, user.social_user)

    @method_decorator(csrf_protect)  # just to be sure csrf is not disabled
    def post(self, request, *args, **kwargs):
        return super(SocialSessionAuthView, self).post(request, *args, **kwargs)


class SocialTokenOnlyAuthView(BaseSocialAuthView):
    serializer_class = TokenSerializer


class SocialTokenUserAuthView(BaseSocialAuthView):
    serializer_class = UserTokenSerializer
