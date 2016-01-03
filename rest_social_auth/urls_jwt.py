from django.conf.urls import url

from . import views


urlpatterns = (
    # returns jwt + user_data
    url(r'^social/jwt_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTUserAuthView.as_view(),
        name='login_social_jwt_user'),

    # returns jwt only
    url(r'^social/jwt/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTOnlyAuthView.as_view(),
        name='login_social_jwt'),)
