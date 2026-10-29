import json
from urllib.parse import urlencode

import responses
from django.test import override_settings
from social_core.backends.facebook import API_VERSION
from social_core.backends.utils import load_backends
from social_core.utils import module_member

from rest_social_auth import views


class RestSocialMixin:
    access_token_status = 200
    access_token_body = json.dumps({'access_token': 'foobar', 'token_type': 'bearer'})
    email = 'example@mail.com'

    def setUp(self):
        super().setUp()
        responses.start()
        self.addCleanup(responses.stop)
        self.addCleanup(responses.reset)
        settings = override_settings(**{
            'SOCIAL_AUTH_' + self.provider.upper() + '_KEY': 'test-key',
            'SOCIAL_AUTH_' + self.provider.upper() + '_SECRET': 'test-secret',
        })
        settings.enable()
        self.addCleanup(settings.disable)
        load_backends((self.backend_path,), force_load=True)
        self.strategy = views.load_strategy()
        self.backend = module_member(self.backend_path)(self.strategy, redirect_uri='/')
        self.do_rest_login()

    def setup_api_mocks(self):
        responses.reset()
        responses.add(
            self.backend.ACCESS_TOKEN_METHOD,
            self.backend.access_token_url(),
            body=self.access_token_body,
            status=self.access_token_status,
        )
        responses.add(responses.GET, self.user_data_url, body=self.user_data_body, status=200)

    def do_rest_login(self):
        self.setup_api_mocks()


class BaseFacebookAPITestCase(RestSocialMixin):
    provider = 'facebook'
    backend_path = 'social_core.backends.facebook.FacebookOAuth2'
    user_data_url = f'https://graph.facebook.com/v{API_VERSION}/me'
    user_data_body = json.dumps({
        'id': '110011001100010',
        'name': 'Foo Bar',
        'first_name': 'Foo',
        'last_name': 'Bar',
        'email': RestSocialMixin.email,
    })


class BaseTwitterApiTestCase(RestSocialMixin):
    provider = 'twitter'
    backend_path = 'social_core.backends.twitter.TwitterOAuth'
    user_data_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    request_token_body = urlencode({
        'oauth_token': 'foobar',
        'oauth_token_secret': 'foobar-secret',
        'oauth_callback_confirmed': 'true',
    })
    access_token_body = urlencode({
        'oauth_token': 'foobar',
        'oauth_token_secret': 'foobar-secret',
    })
    user_data_body = json.dumps({
        'id': 10101010,
        'screen_name': 'foobar',
        'name': 'Foo Bar',
        'email': RestSocialMixin.email,
        'profile_image_url': 'https://example.com/avatar.jpg',
    })

    def do_rest_login(self):
        super().do_rest_login()
        responses.add(
            self.backend.REQUEST_TOKEN_METHOD,
            self.backend.REQUEST_TOKEN_URL,
            body=self.request_token_body,
            status=200,
        )
