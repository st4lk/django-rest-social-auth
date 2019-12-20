from django.http import HttpRequest
from social_django.strategy import DjangoStrategy


class DRFStrategy(DjangoStrategy):

    def __init__(self, storage, request=None, tpl=None):
        self.request = request
        self.session = {}

        if request:
            try:
                self.session = request.session
            except AttributeError:
                # in case of token auth session can be disabled at all
                pass

        super(DjangoStrategy, self).__init__(storage, tpl)

    def request_data(self, merge=True):
        if self.request:
            return getattr(self.request, 'auth_data', {})
        else:
            return {}

    def clean_authenticate_args(self, *args, **kwargs):
        """Cleanup request argument if present, which is passed to
        authenticate as for Django 1.11"""
        if len(args) > 0 and (
                isinstance(args[0], HttpRequest) or
                isinstance(getattr(args[0], '_request', None), HttpRequest)  # rest_framework.request.Request
        ):
            print('123!!! clean_authenticate_args')
            kwargs['request'], args = args[0], args[1:]
        return args, kwargs
