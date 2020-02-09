from django.test import override_settings
from django.urls import reverse
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from rest_framework.test import APITestCase
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


knox_override_settings = dict(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'rest_framework',
        'social_django',
        'rest_social_auth',
        'knox',  # For django-rest-knox
        'users',
    ],
    MIDDLEWARE=[
    ],
)


@override_settings(**knox_override_settings)
class TestSocialAuth1Knox(APITestCase, BaseTwitterApiTestCase):

    def test_login_social_oauth1_knox(self):
        resp = self.client.post(
            reverse('login_social_knox_user'), data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_knox_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)


@override_settings(**knox_override_settings)
class TestSocialAuth2Knox(APITestCase, BaseFacebookAPITestCase):

    def _check_login_social_knox_only(self, url, data):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # check token valid
        knox_auth = KnoxTokenAuthentication()
        user, auth_data = knox_auth.authenticate_credentials(resp.data['token'].encode('utf8'))
        self.assertEqual(user.email, self.email)

    def _check_login_social_knox_user(self, url, data):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token valid
        knox_auth = KnoxTokenAuthentication()
        user, auth_data = knox_auth.authenticate_credentials(resp.data['token'].encode('utf8'))
        self.assertEqual(user.email, self.email)

    def test_login_social_knox_only(self):
        self._check_login_social_knox_only(
            reverse('login_social_knox'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_knox_only_provider_in_url(self):
        self._check_login_social_knox_only(
            reverse('login_social_knox', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_knox_user(self):
        self._check_login_social_knox_user(
            reverse('login_social_knox_user'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'})

    def test_login_social_knox_user_provider_in_url(self):
        self._check_login_social_knox_user(
            reverse('login_social_knox_user', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'})
