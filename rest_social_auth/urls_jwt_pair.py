from django.urls import re_path

from . import views


urlpatterns = (
    # returns token only
    re_path(r'^social/jwt-pair/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTPairOnlyAuthView.as_view(),
            name='login_social_jwt_pair'),
    # returns token + user_data
    re_path(r'^social/jwt-pair-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialJWTPairUserAuthView.as_view(),
            name='login_social_jwt_pair_user'),
)
