from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings as jwt_api_settings
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


jwt_override_settings = dict(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'rest_framework',
        'social_django',
        'rest_social_auth',
        'users',
    ],
    MIDDLEWARE=[],
)


@override_settings(**jwt_override_settings)
class TestSocialAuth1JWT(APITestCase, BaseTwitterApiTestCase):

    def test_login_social_oauth1_jwt(self):
        resp = self.client.post(
            reverse('login_social_jwt_user'), data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_jwt_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)


@override_settings(**jwt_override_settings)
class TestSocialAuth2JWT(APITestCase, BaseFacebookAPITestCase):

    def _check_login_social_jwt_only(self, url, data):
        jwt_decode_handler = jwt_api_settings.JWT_DECODE_HANDLER
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # check token valid
        jwt_data = jwt_decode_handler(resp.data['token'])
        self.assertEqual(jwt_data['email'], self.email)

    def _check_login_social_jwt_user(self, url, data):
        jwt_decode_handler = jwt_api_settings.JWT_DECODE_HANDLER
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token valid
        jwt_data = jwt_decode_handler(resp.data['token'])
        self.assertEqual(jwt_data['email'], self.email)

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
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'},
        )
