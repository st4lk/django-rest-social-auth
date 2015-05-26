# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    # returns token + user_data
    url(r'^social/token_user/$', views.SocialTokenUserAuthView.as_view(),
        name='login_social_token_user'),
    # returns token only
    url(r'^social/token/$', views.SocialTokenOnlyAuthView.as_view(),
        name='login_social_token'),
)
