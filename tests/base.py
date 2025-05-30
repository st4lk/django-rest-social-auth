import json

import responses
from social_core.backends.utils import load_backends
from social_core.tests.backends.test_facebook import FacebookOAuth2Test
from social_core.tests.backends.test_twitter import TwitterOAuth1Test
from social_core.utils import module_member

from social_core.tests.models import (
    TestAssociation,
    TestCode,
    TestNonce,
    TestUserSocialAuth,
    User,
)

from rest_social_auth import views


# don't run third party tests
for attr in (attr for attr in dir(FacebookOAuth2Test) if attr.startswith('test_')):
    try:
        delattr(FacebookOAuth2Test, attr)
    except AttributeError:
        pass
for attr in (attr for attr in dir(TwitterOAuth1Test) if attr.startswith('test_')):
    try:
        delattr(TwitterOAuth1Test, attr)
    except AttributeError:
        pass


class RestSocialMixin:
    def setUp(self):
        responses.start()
        Backend = module_member(self.backend_path)
        self.strategy = views.load_strategy()
        self.backend = Backend(self.strategy, redirect_uri=self.complete_url)
        self.name = self.backend.name.upper().replace("-", "_")
        self.complete_url = self.strategy.build_absolute_uri(
            self.raw_complete_url.format(self.backend.name)
        )
        backends = (self.backend_path, )
        load_backends(backends, force_load=True)
        User.reset_cache()
        TestUserSocialAuth.reset_cache()
        TestNonce.reset_cache()
        TestAssociation.reset_cache()
        TestCode.reset_cache()

        user_data_body = json.loads(self.user_data_body)
        self.email = 'example@mail.com'
        user_data_body['email'] = self.email
        self.user_data_body = json.dumps(user_data_body)

        self.do_rest_login()

    def tearDown(self):
        responses.stop()
        responses.reset()
        self.backend = None
        self.strategy = None
        self.name = None
        self.complete_url = None
        User.reset_cache()
        TestUserSocialAuth.reset_cache()
        TestNonce.reset_cache()
        TestAssociation.reset_cache()
        TestCode.reset_cache()


class BaseFacebookAPITestCase(RestSocialMixin, FacebookOAuth2Test):

    def do_rest_login(self):
        start_url = self.backend.start().url
        self.auth_handlers(start_url)
        self.pre_complete_callback(start_url)

    def setup_api_mocks(self):
        # Add missing mocks for access token and user data endpoints
        responses.reset()
        responses.add(
            responses.GET,
            self.backend.access_token_url(),
            body=self.access_token_body,
            status=self.access_token_status
        )
        responses.add(
            responses.GET,
            self.user_data_url,
            body=self.user_data_body,
            status=200
        )


class BaseTwitterApiTestCase(RestSocialMixin, TwitterOAuth1Test):

    def do_rest_login(self):
        self.request_token_handler()
        start_url = self.backend.start().url
        self.auth_handlers(start_url)
        self.pre_complete_callback(start_url)
