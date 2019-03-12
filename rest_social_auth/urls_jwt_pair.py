from django.conf.urls import url

from . import views


urlpatterns = (
    # returns token only
    url(r'^social/jwt-pair/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTPairOnlyAuthView.as_view(),
        name='login_social_jwt_pair'),
    # returns token + user_data
    url(r'^social/jwt-pair-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTPairUserAuthView.as_view(),
        name='login_social_jwt_pair_user'),
)
