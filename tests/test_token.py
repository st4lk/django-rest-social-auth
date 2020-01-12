import json

from django.test import modify_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


token_modify_settings = dict(
    INSTALLED_APPS={
        'remove': [
            'django.contrib.sessions',
            'knox',
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


class TestSocialAuth1Token(APITestCase, BaseTwitterApiTestCase):

    def test_login_social_oauth1_token(self):
        """
        Currently oauth1 works only if session is enabled.
        Probably it is possible to make it work without session, but
        it will be needed to change the logic in python-social-auth.
        """
        resp = self.client.post(
            reverse('login_social_token_user'), data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_token_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)


class TestSocialAuth2Token(APITestCase, BaseFacebookAPITestCase):

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

    def test_user_login_with_no_email(self):
        user_data_body = json.loads(self.user_data_body)
        user_data_body['email'] = ''
        self.user_data_body = json.dumps(user_data_body)
        self.do_rest_login()
        resp = self.client.post(
            reverse('login_social_token'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)
