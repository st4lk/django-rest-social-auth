# -*- coding: utf-8 -*-
from social.strategies.django_strategy import DjangoStrategy


class DRFStrategy(DjangoStrategy):
    def request_data(self, merge=True):
        if self.request:
            return getattr(self.request, 'auth_data', {})
        else:
            return {}
