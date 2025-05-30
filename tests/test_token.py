import json

from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from social_core.utils import parse_qs

from .base import BaseFacebookAPITestCase, BaseTwitterApiTestCase


token_override_settings = dict(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'rest_framework',
        'rest_framework.authtoken',
        'social_django',
        'rest_social_auth',
        'users',
    ],
    MIDDLEWARE=[],
    SOCIAL_AUTH_PIPELINE=(
        'users.social_pipeline.auto_logout',  # custom action
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'users.social_pipeline.check_for_email',  # custom action
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details',
        'users.social_pipeline.save_avatar',  # custom action
    ),
)


@override_settings(**token_override_settings)
class TestSocialAuth1Token(APITestCase, BaseTwitterApiTestCase):

    def test_login_social_oauth1_token(self):
        url = reverse('login_social_token_user')
        resp = self.client.post(url, data={'provider': 'twitter'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, parse_qs(self.request_token_body))
        resp = self.client.post(reverse('login_social_token_user'), data={
            'provider': 'twitter',
            'oauth_token': 'foobar',
            'oauth_verifier': 'overifier'
        })
        self.assertEqual(resp.status_code, 200)


@override_settings(**token_override_settings)
class TestSocialAuth2Token(APITestCase, BaseFacebookAPITestCase):

    def _check_login_social_token_user(self, url, data):
        self.setup_api_mocks()
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], self.email)
        # check token exists
        token = Token.objects.get(key=resp.data['token'])
        # check user is created
        self.assertEqual(token.user.email, self.email)

    def _check_login_social_token_only(self, url, data):
        self.setup_api_mocks()
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
        # Modify user data to have no email BEFORE setting up the test
        user_data_body = json.loads(self.user_data_body)
        user_data_body['email'] = ''
        self.user_data_body = json.dumps(user_data_body)

        # Set up mocks and do the rest login
        self.do_rest_login()
        self.setup_api_mocks()

        resp = self.client.post(
            reverse('login_social_token'),
            data={'provider': 'facebook', 'code': '3D52VoM1uiw94a1ETnGvYlCw'},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.data)
