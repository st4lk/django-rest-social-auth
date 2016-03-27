import json
import logging
try:
    from urlparse import parse_qsl, urlparse
except ImportError:
    # python 3
    from urllib.parse import parse_qsl, urlparse

from mock import patch
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from httpretty import HTTPretty
from social.utils import module_member, parse_qs
from social.backends.utils import load_backends
from social.tests.backends.test_facebook import FacebookOAuth2Test
from social.tests.backends.test_twitter import TwitterOAuth1Test

from rest_social_auth import views
from .utils import modify_settings


l = logging.getLogger(__name__)


# don't run third party tests
for attr in (attr for attr in dir(FacebookOAuth2Test) if attr.startswith('test_')):
    delattr(FacebookOAuth2Test, attr)
for attr in (attr for attr in dir(TwitterOAuth1Test) if attr.startswith('test_')):
    delattr(TwitterOAuth1Test, attr)


session_modify_settings = dict(
    INSTALLED_APPS={
        'remove': [
            'rest_framework.authtoken',
        ]
    },
)


token_modify_settings = dict(
    INSTALLED_APPS={
        'remove': [
            'django.contrib.sessions'
        ]
    },
    MIDDLEWARE_CLASSES={
        'remove': [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
    }
)


jwt_modify_settings = dict(
    INSTALLED_APPS={
        'remove': [
            'django.contrib.sessions',
            'rest_framework.authtoken',
        ]
    },
    MIDDLEWARE_CLASSES={
        'remove': [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
    }
)


class RestSocialMixin(object):
    def setUp(self):
        HTTPretty.enable()
        Backend = module_member(self.backend_path)
        self.strategy = views.load_strategy()
        self.backend = Backend(self.strategy, redirect_uri=self.complete_url)
        self.name = self.backend.name.upper().replace('-', '_')
        self.complete_url = self.strategy.build_absolute_uri(
            self.raw_complete_url.format(self.backend.name)
        )
        backends = (self.backend_path, )
        load_backends(backends, force_load=True)

        user_data_body = json.loads(self.user_data_body)
        self.email = 'example@mail.com'
        user_data_body['email'] = self.email
        self.user_data_body = json.dumps(user_data_body)

        self.do_rest_login()

    def tearDown(self):
        HTTPretty.disable()
        HTTPretty.reset()
        self.backend = None
        self.strategy = None
        self.name = None
        self.complete_url = None


class BaseFacebookAPITestCase(RestSocialMixin, FacebookOAuth2Test):

    def do_rest_login(self):
        start_url = self.backend.start().url
        self.auth_handlers(start_url)


class BaseTwitterApiTestCase(RestSocialMixin, TwitterOAuth1Test):

    def do_rest_login(self):
        self.request_token_handler()
        start_url = self.backend.start().url
        self.auth_handlers(start_url)


class TestSocialAuth1(APITestCase, BaseTwitterApiTestCase):

    @modify_settings(**session_modify_settings)
    def test_login_social_oauth1_session(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_session'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)

    def test_login_social_oauth1_token(self):
        """
        Currently oauth1 works only if session is enabled.
        Probably it is possible to make it work without session, but
        it will be needed to change the logic in python-social-auth.
        """
        resp = self.client.post(reverse('login_social_token_user'),
            data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_token_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)

    @modify_settings(INSTALLED_APPS={'remove': ['rest_framework.authtoken', ]})
    def test_login_social_oauth1_jwt(self):
        """
        Currently oauth1 works only if session is enabled.
        Probably it is possible to make it work without session, but
        it will be needed to change the logic in python-social-auth.
        """
        try:
            import rest_framework_jwt
        except ImportError:
            return
        assert rest_framework_jwt is not None
        resp = self.client.post(reverse('login_social_jwt_user'),
            data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_token_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)


class TestSocialAuth2(APITestCase, BaseFacebookAPITestCase):

    @modify_settings(**session_modify_settings)
    def _check_login_social_session(self, url, data):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check cookies are set
        self.assertTrue('sessionid' in resp.cookies)
        # check user is created
        self.assertTrue(
            get_user_model().objects.filter(email=self.email).exists())

    @modify_settings(**token_modify_settings)
    def _check_login_social_token_user(self, url, data):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token exists
        token = Token.objects.get(key=resp.data['token'])
        # check user is created
        self.assertEqual(token.user.email, self.email)

    @modify_settings(**token_modify_settings)
    def _check_login_social_token_only(self, url, data):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # check token exists
        token = Token.objects.get(key=resp.data['token'])
        # check user is created
        self.assertEqual(token.user.email, self.email)

    @modify_settings(**jwt_modify_settings)
    def _check_login_social_jwt_only(self, url, data):
        try:
            from rest_framework_jwt.settings import api_settings
        except ImportError:
            return
        jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # check token valid
        jwt_data = jwt_decode_handler(resp.data['token'])
        self.assertEqual(jwt_data['email'], self.email)

    @modify_settings(**jwt_modify_settings)
    def _check_login_social_jwt_user(self, url, data):
        try:
            from rest_framework_jwt.settings import api_settings
        except ImportError:
            return
        jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token valid
        jwt_data = jwt_decode_handler(resp.data['token'])
        self.assertEqual(jwt_data['email'], self.email)

    def test_login_social_session(self):
        self._check_login_social_session(
            reverse('login_social_session'),
            {'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_session_provider_in_url(self):
        self._check_login_social_session(
            reverse('login_social_session', kwargs={'provider': 'facebook'}),
            {'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_token_user(self):
        self._check_login_social_token_user(
            reverse('login_social_token_user'),
            {'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_token_user_provider_in_url(self):
        self._check_login_social_token_user(
            reverse('login_social_token_user', kwargs={'provider': 'facebook'}),
            {'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_token_only(self):
        self._check_login_social_token_only(
            reverse('login_social_token'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_token_only_provider_in_url(self):
        self._check_login_social_token_only(
            reverse('login_social_token', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_jwt_only(self):
        self._check_login_social_jwt_only(
            reverse('login_social_jwt'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_jwt_only_provider_in_url(self):
        self._check_login_social_jwt_only(
            reverse('login_social_jwt', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_jwt_user(self):
        self._check_login_social_jwt_user(
            reverse('login_social_jwt_user'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_jwt_user_provider_in_url(self):
        self._check_login_social_jwt_user(
            reverse('login_social_jwt_user', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_no_provider_session(self):
        resp = self.client.post(
            reverse('login_social_session'),
            {'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 400)

    def test_unknown_provider_session(self):
        resp = self.client.post(
            reverse('login_social_session', kwargs={'provider': 'unknown'}),
            {'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 404)

    def test_login_social_http_origin(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            HTTP_ORIGIN="http://frontend.com")
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual(url_params['redirect_uri'], "http://frontend.com/")

    @override_settings(REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI='http://myproject.com/')
    def test_login_absolute_redirect(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual('http://myproject.com/', url_params['redirect_uri'])

    @override_settings(REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI='http://myproject.com/')
    def test_login_manual_redirect(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw',
                'redirect_uri': 'http://manualdomain.com/'})
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual('http://manualdomain.com/', url_params['redirect_uri'])

    @patch('rest_framework.views.APIView.permission_classes')
    def test_login_social_session_model_permission(self, m_permission_classes):
        setattr(m_permission_classes, '__get__', lambda *args, **kwargs: (DjangoModelPermissionsOrAnonReadOnly, ))
        self._check_login_social_session(
            reverse('login_social_session'),
            {'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})


class TestSocialAuth2Error(APITestCase, BaseFacebookAPITestCase):
    access_token_status = 400

    def test_login_oauth_provider_error(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 400)


class TestSocialAuth2HTTPError(APITestCase, BaseFacebookAPITestCase):
    access_token_status = 401

    def test_login_oauth_provider_http_error(self):
        resp = self.client.post(reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 400)
