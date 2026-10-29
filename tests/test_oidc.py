import time
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from django.test import RequestFactory, override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.backends.utils import load_backends

from rest_social_auth.views import load_strategy


@override_settings(
    AUTHENTICATION_BACKENDS=('social_core.backends.open_id_connect.OpenIdConnectAuth',),
    SOCIAL_AUTH_OIDC_OIDC_ENDPOINT='https://id.example.com',
    SOCIAL_AUTH_OIDC_KEY='test-client',
    SOCIAL_AUTH_OIDC_SECRET='test-secret',
)
class TestOpenIdConnect(APITestCase):
    def setUp(self):
        super().setUp()
        responses.start()
        self.addCleanup(responses.stop)
        self.addCleanup(responses.reset)
        load_backends(('social_core.backends.open_id_connect.OpenIdConnectAuth',), force_load=True)
        responses.get('https://id.example.com/.well-known/openid-configuration', json={
            'issuer': 'https://id.example.com',
            'authorization_endpoint': 'https://id.example.com/authorize',
            'token_endpoint': 'https://id.example.com/token',
            'userinfo_endpoint': 'https://id.example.com/userinfo',
        })
        responses.post('https://id.example.com/token', json={
            'access_token': 'test-access-token', 'id_token': 'test-id-token',
        })
        responses.get('https://id.example.com/userinfo', json={
            'sub': 'victim', 'email': 'victim@example.com', 'name': 'Test User',
        })
        request = RequestFactory().get('/')
        request.session = self.client.session
        backend = OpenIdConnectAuth(load_strategy(request), redirect_uri='http://testserver/')
        params = parse_qs(urlparse(backend.auth_url()).query)
        request.session.save()
        self.data = {'provider': 'oidc', 'code': 'authorization-code', 'state': params['state'][0]}
        self.claims = {
            'sub': 'victim', 'iss': 'https://id.example.com', 'aud': 'test-client',
            'iat': int(time.time()), 'exp': int(time.time()) + 300,
            'nonce': params['nonce'][0],
        }
        # Keep upstream state and nonce validation; only bypass JWT signature decoding.
        decoder = patch.object(OpenIdConnectAuth, 'decode_and_validate_id_token',
                               return_value=self.claims)
        decoder.start()
        self.addCleanup(decoder.stop)

    def complete(self, client=None):
        return (client or self.client).post(reverse('login_social_token_user'), self.data)

    def test_same_browser_can_complete_once(self):
        response = self.complete()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'victim@example.com')
        self.assertEqual(self.complete().status_code, 400)

    def test_other_browser_cannot_redeem_code(self):
        self.assertEqual(self.complete(APIClient()).status_code, 400)
        self.assertFalse(any(call.request.url.endswith('/token') for call in responses.calls))
        self.assertEqual(self.complete().status_code, 200)

    def test_wrong_nonce_is_rejected(self):
        self.claims['nonce'] = 'another-login-nonce'
        self.assertEqual(self.complete().status_code, 400)

    def test_missing_state_is_rejected(self):
        self.data.pop('state')
        self.assertEqual(self.complete().status_code, 400)
