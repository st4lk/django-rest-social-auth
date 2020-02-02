try:
    from urlparse import parse_qsl, urlparse
except ImportError:
    # python 3
    from urllib.parse import parse_qsl, urlparse

from mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import modify_settings
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from httpretty import HTTPretty
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


session_modify_settings = dict(
    INSTALLED_APPS={
        'remove': [
            'rest_framework.authtoken',
            'knox',
        ]
    },
)


class TestSocialAuth1(APITestCase, BaseTwitterApiTestCase):

    @modify_settings(**session_modify_settings)
    def test_login_social_oauth1_session(self):
        resp = self.client.post(
            reverse('login_social_session'), data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_session'), data={
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

    def test_login_social_session(self):
        self._check_login_social_session(
            reverse('login_social_session'),
            {'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_session_provider_in_url(self):
        self._check_login_social_session(
            reverse('login_social_session', kwargs={'provider': 'facebook'}),
            {'code': '3D52VoM1uiw94a1ETnGvYlCw'})

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
        resp = self.client.post(
            reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            HTTP_ORIGIN="http://frontend.com")
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual(url_params['redirect_uri'], "http://frontend.com/")

    @override_settings(REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI='http://myproject.com/')
    def test_login_absolute_redirect(self):
        resp = self.client.post(
            reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual('http://myproject.com/', url_params['redirect_uri'])

    @override_settings(REST_SOCIAL_OAUTH_ABSOLUTE_REDIRECT_URI='http://myproject.com/')
    def test_login_manual_redirect(self):
        resp = self.client.post(
            reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw',
                  'redirect_uri': 'http://manualdomain.com/'})
        self.assertEqual(resp.status_code, 200)
        url_params = dict(parse_qsl(urlparse(HTTPretty.latest_requests[0].path).query))
        self.assertEqual('http://manualdomain.com/', url_params['redirect_uri'])

    @patch('rest_framework.views.APIView.permission_classes')
    def test_login_social_session_model_permission(self, m_permission_classes):
        setattr(
            m_permission_classes,
            '__get__',
            lambda *args, **kwargs: (DjangoModelPermissionsOrAnonReadOnly,),
        )
        self._check_login_social_session(
            reverse('login_social_session'),
            {'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})


class TestSocialAuth2Error(APITestCase, BaseFacebookAPITestCase):
    access_token_status = 400

    def test_login_oauth_provider_error(self):
        resp = self.client.post(
            reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 400)


class TestSocialAuth2HTTPError(APITestCase, BaseFacebookAPITestCase):
    access_token_status = 401

    def test_login_oauth_provider_http_error(self):
        resp = self.client.post(
            reverse('login_social_session'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})
        self.assertEqual(resp.status_code, 400)
