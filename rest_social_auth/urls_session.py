from django.urls import re_path

from . import views


urlpatterns = (
    re_path(r'^social/session/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialSessionAuthView.as_view(),
            name='login_social_session'),)
