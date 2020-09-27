from django.urls import re_path

from . import views


urlpatterns = (
    # returns jwt + user_data
    re_path(r'^social/jwt_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTUserAuthView.as_view(),
            name='login_social_jwt_user'),

    # returns jwt only
    re_path(r'^social/jwt/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTOnlyAuthView.as_view(),
            name='login_social_jwt'),)
