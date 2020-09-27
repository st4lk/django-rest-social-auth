from django.urls import re_path

from . import views


urlpatterns = (
    # returns token + user_data
    re_path(r'^social/token_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialTokenUserAuthView.as_view(),
            name='login_social_token_user'),

    # returns token only
    re_path(r'^social/token/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialTokenOnlyAuthView.as_view(),
            name='login_social_token'),)
