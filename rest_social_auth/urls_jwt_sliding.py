from django.urls import re_path

from . import views


urlpatterns = (
    # returns token only
    re_path(r'^social/jwt-sliding/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTSlidingOnlyAuthView.as_view(),
            name='login_social_jwt_sliding'),
    # returns token + user_data
    re_path(r'^social/jwt-sliding-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTSlidingUserAuthView.as_view(),
            name='login_social_jwt_sliding_user'),
)
