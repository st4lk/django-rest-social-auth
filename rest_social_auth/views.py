import logging
import warnings

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from urllib.parse import urljoin, urlencode, urlparse
from social_django.utils import psa, STORAGE
from social_django.views import _do_login as social_auth_login
from social_core.backends.oauth import BaseOAuth1
from social_core.utils import get_strategy, parse_qs, user_is_authenticated, setting_name
from social_core.exceptions import AuthException, SocialAuthBaseException
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from requests.exceptions import HTTPError

from .serializers import (
    JWTPairSerializer,
    JWTSlidingSerializer,
    KnoxSerializer,
    OAuth1InputSerializer,
    OAuth2InputSerializer,
    TokenSerializer,
    UserJWTSlidingSerializer,
    UserKnoxSerializer,
    UserJWTPairSerializer,
    UserSerializer,
    UserTokenSerializer,
)


logger = logging.getLogger(__name__)


REDIRECT_URI = getattr(settings, 'REST_SOCIAL_OAUTH_REDIRECT_URI', '/')
DOMAIN_FROM_ORIGIN = getattr(settings, 'REST_SOCIAL_DOMAIN_FROM_ORIGIN', True)
LOG_AUTH_EXCEPTIONS = getattr(settings, 'REST_SOCIAL_LOG_AUTH_EXCEPTIONS', True)
VERBOSE_ERRORS = getattr(settings, 'REST_SOCIAL_VERBOSE_ERRORS', False)
STRATEGY = getattr(settings, setting_name('STRATEGY'), 'rest_social_auth.strategy.DRFStrategy')


def load_strategy(request=None):
    return get_strategy(STRATEGY, STORAGE, request)


@psa(REDIRECT_URI, load_strategy=load_strategy)
def decorate_request(request, backend):
    pass


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

    oauth1_serializer_class_in = OAuth1InputSerializer
    oauth2_serializer_class_in = OAuth2InputSerializer
    serializer_class = None
    permission_classes = (AllowAny, )

    def oauth_v1(self):
        assert hasattr(self.request, 'backend'), 'Don\'t call this method before decorate_request'
        return isinstance(self.request.backend, BaseOAuth1)

    def get_serializer_class_in(self):
        if self.oauth_v1():
            return self.oauth1_serializer_class_in
        return self.oauth2_serializer_class_in

    def get_serializer_in(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class_in()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_in_data(self):
        """
        Compile the incoming data into a form fit for the serializer_in class.
        :return: Data for serializer in the form of a dictionary with 'provider' and 'code' keys.
        """
        return self.request.data.copy()

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        input_data = self.get_serializer_in_data()
        provider_name = self.get_provider_name(input_data)
        if not provider_name:
            return self.respond_error("Provider is not specified")
        self.set_input_data(request, input_data)
        decorate_request(request, provider_name)
        serializer_in = self.get_serializer_in(data=input_data)
        if self.oauth_v1() and request.backend.OAUTH_TOKEN_PARAMETER_NAME not in input_data:
            # oauth1 first stage (1st is get request_token, 2nd is get access_token)
            manual_redirect_uri = self.request.auth_data.pop('redirect_uri', None)
            manual_redirect_uri = self.get_redirect_uri(manual_redirect_uri)
            if manual_redirect_uri:
                self.request.backend.redirect_uri = manual_redirect_uri
            request_token = parse_qs(request.backend.set_unauthorized_token())
            return Response(request_token)
        serializer_in.is_valid(raise_exception=True)
        try:
            user = self.get_object()
        except (AuthException, HTTPError) as e:
            return self.respond_error(e)
        if isinstance(user, HttpResponse):
            # error happened and pipeline returned HttpResponse instead of user
            return user
        resp_data = self.get_serializer(instance=user)
        self.do_login(request.backend, user)
        return Response(resp_data.data)

    def get_object(self):
        user = self.request.user
        manual_redirect_uri = self.request.auth_data.pop('redirect_uri', None)
        manual_redirect_uri = self.get_redirect_uri(manual_redirect_uri)
        if manual_redirect_uri:
            self.request.backend.redirect_uri = manual_redirect_uri
        elif DOMAIN_FROM_ORIGIN:
            origin = self.request.strategy.request.META.get('HTTP_ORIGIN')
            if origin:
                relative_path = urlparse(self.request.backend.redirect_uri).path
                url = urlparse(origin)
                origin_scheme_host = f"{url.scheme}://{url.netloc}"
                location = urljoin(origin_scheme_host, relative_path)
                self.request.backend.redirect_uri = iri_to_uri(location)
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
        self.request.backend.REDIRECT_STATE = False
        self.request.backend.STATE_PARAMETER = False

        if self.oauth_v1():
            self.save_token_param_in_session()

        user = self.request.backend.complete(user=user, request=self.request)
        return user

    def save_token_param_in_session(self):
        """
        Save token param in strategy's session.
        This method will allow to use token auth with OAuth1 even if session is not enabled in
        django settings (social_core expects that session is enabled).
        """
        backend = self.request.backend
        session_token_name = backend.name + backend.UNATHORIZED_TOKEN_SUFIX
        session = self.request.strategy.session
        if (
            (isinstance(session, dict) and session_token_name not in session) or
            not session.exists(session_token_name)
        ):
            oauth1_token_param = backend.data.get(backend.OAUTH_TOKEN_PARAMETER_NAME)
            session[session_token_name] = [
                urlencode({
                    backend.OAUTH_TOKEN_PARAMETER_NAME: oauth1_token_param,
                    'oauth_token_secret': backend.data.get('oauth_token_secret')
                })
            ]

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
            manual_redirect_uri = getattr(
                settings, 'REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI', None)
        return manual_redirect_uri

    def get_provider_name(self, input_data):
        if self.kwargs.get('provider'):
            return self.kwargs['provider']
        return input_data.get('provider')

    def respond_error(self, error):
        message = error if isinstance(error, str) else ''
        if isinstance(error, Exception):
            if not isinstance(error, AuthException) or LOG_AUTH_EXCEPTIONS:
                self.log_exception(error)
            if VERBOSE_ERRORS:
                if hasattr(error, 'response'):
                    try:
                        message = error.response.json()['error']
                        if isinstance(message, dict) and 'message' in message:
                            message = message['message']
                        elif isinstance(message, list) and len(message):
                            message = message[0]
                    except (KeyError, TypeError):
                        pass
                # As a fallback, if no valid message was captured, covert the exception to string
                # because most of the social-core exceptions implement a valid conversion.
                if isinstance(error, SocialAuthBaseException) and not message:
                    message = str(error)
        else:
            logger.error(error)
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

    def log_exception(self, error):
        err_msg = error.args[0] if error.args else ''
        if getattr(error, 'response', None) is not None:
            try:
                err_data = error.response.json()
            except (ValueError, AttributeError):
                logger.error('%s; %s', error, err_msg)
            else:
                logger.error('%s; %s; %s', error, err_msg, err_data)
        else:
            logger.exception('{%s}; {%s}', error, err_msg)


class SocialSessionAuthView(BaseSocialAuthView):
    serializer_class = UserSerializer

    def do_login(self, backend, user):
        social_auth_login(backend, user, user.social_user)

    @method_decorator(csrf_protect)  # just to be sure csrf is not disabled
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SocialTokenOnlyAuthView(BaseSocialAuthView):
    serializer_class = TokenSerializer
    authentication_classes = (TokenAuthentication, )


class SocialTokenUserAuthView(BaseSocialAuthView):
    serializer_class = UserTokenSerializer
    authentication_classes = (TokenAuthentication, )


class KnoxAuthMixin:
    def get_authenticators(self):
        try:
            from knox.auth import TokenAuthentication
        except ImportError:
            warnings.warn(
                'django-rest-knox must be installed for Knox authentication',
                ImportWarning,
            )
            raise

        return [TokenAuthentication()]


class SocialKnoxOnlyAuthView(KnoxAuthMixin, BaseSocialAuthView):
    serializer_class = KnoxSerializer


class SocialKnoxUserAuthView(KnoxAuthMixin, BaseSocialAuthView):
    serializer_class = UserKnoxSerializer


class SimpleJWTAuthMixin:
    def get_authenticators(self):
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
        except ImportError:
            warnings.warn(
                'django-rest-framework-simplejwt must be installed for JWT authentication',
                ImportWarning,
            )
            raise

        return [JWTAuthentication()]


class SocialJWTPairOnlyAuthView(SimpleJWTAuthMixin, BaseSocialAuthView):
    serializer_class = JWTPairSerializer


class SocialJWTPairUserAuthView(SimpleJWTAuthMixin, BaseSocialAuthView):
    serializer_class = UserJWTPairSerializer


class SocialJWTSlidingOnlyAuthView(SimpleJWTAuthMixin, BaseSocialAuthView):
    serializer_class = JWTSlidingSerializer


class SocialJWTSlidingUserAuthView(SimpleJWTAuthMixin, BaseSocialAuthView):
    serializer_class = UserJWTSlidingSerializer
