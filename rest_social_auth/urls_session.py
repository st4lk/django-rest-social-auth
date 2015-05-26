# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^social/session/$', views.SocialSessionAuthView.as_view(),
        name='login_social_session'),
)
