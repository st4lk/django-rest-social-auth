from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.authentication import JWTAuthentication
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


jwt_simple_override_settings = dict(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'rest_framework',
        'social_django',
        'rest_social_auth',
        'users',
    ],
    MIDDLEWARE=[],
)


@override_settings(**jwt_simple_override_settings)
class TestSocialAuth1SimpleJWT(APITestCase, BaseTwitterApiTestCase):

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


@override_settings(**jwt_simple_override_settings)
class TestSocialAuth2SimpleJWT(APITestCase, BaseFacebookAPITestCase):

    def _check_login_social_simple_jwt_only(self, url, data, token_type):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # check token valid
        jwt_auth = JWTAuthentication()
        token_instance = jwt_auth.get_validated_token(resp.data['token'])
        self.assertEqual(token_instance['token_type'], token_type)

    def _check_login_social_simple_jwt_user(self, url, data, token_type):
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token valid
        jwt_auth = JWTAuthentication()
        token_instance = jwt_auth.get_validated_token(resp.data['token'])
        self.assertEqual(token_instance['token_type'], token_type)
        self.assertEqual(token_instance['email'], self.email)

    def test_login_social_simple_jwt_pair_only(self):
        self._check_login_social_simple_jwt_only(
            reverse('login_social_jwt_pair'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='access',
        )

    def test_login_social_simple_jwt_pair_only_provider_in_url(self):
        self._check_login_social_simple_jwt_only(
            reverse('login_social_jwt_pair', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='access',
        )

    def test_login_social_simple_jwt_pair_user(self):
        self._check_login_social_simple_jwt_user(
            reverse('login_social_jwt_pair_user'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='access',
        )

    def test_login_social_simple_jwt_pair_user_provider_in_url(self):
        self._check_login_social_simple_jwt_user(
            reverse('login_social_jwt_pair_user', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='access',
        )

    def test_login_social_simple_jwt_sliding_only(self):
        self._check_login_social_simple_jwt_only(
            reverse('login_social_jwt_sliding'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='sliding',
        )

    def test_login_social_simple_jwt_sliding_only_provider_in_url(self):
        self._check_login_social_simple_jwt_only(
            reverse('login_social_jwt_sliding', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='sliding',
        )

    def test_login_social_simple_jwt_sliding_user(self):
        self._check_login_social_simple_jwt_user(
            reverse('login_social_jwt_sliding_user'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='sliding',
        )

    def test_login_social_simple_jwt_sliding_user_provider_in_url(self):
        self._check_login_social_simple_jwt_user(
            reverse('login_social_jwt_sliding_user', kwargs={'provider': 'facebook'}),
            data={'code': '3D52VoM1uiw94a1ETnGvYlCw'},
            token_type='sliding',
        )
