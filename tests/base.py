import json

from httpretty import HTTPretty
from social_core.backends.utils import load_backends
from social_core.tests.backends.test_facebook import FacebookOAuth2Test
from social_core.tests.backends.test_twitter import TwitterOAuth1Test
from social_core.utils import module_member

from rest_social_auth import views


# don't run third party tests
for attr in (attr for attr in dir(FacebookOAuth2Test) if attr.startswith('test_')):
    delattr(FacebookOAuth2Test, attr)
for attr in (attr for attr in dir(TwitterOAuth1Test) if attr.startswith('test_')):
    delattr(TwitterOAuth1Test, attr)


class RestSocialMixin:
    def setUp(self):
        HTTPretty.enable(allow_net_connect=False)
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
        self.pre_complete_callback(start_url)


class BaseTwitterApiTestCase(RestSocialMixin, TwitterOAuth1Test):

    def do_rest_login(self):
        self.request_token_handler()
        start_url = self.backend.start().url
        self.auth_handlers(start_url)
        self.pre_complete_callback(start_url)
