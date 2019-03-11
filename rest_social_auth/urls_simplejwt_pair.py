from django.conf.urls import url

from . import views


urlpatterns = (
    # returns token only
    url(r'^social/jwt-pair/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTPairOnlyAuthView.as_view(),
        name='login_social_simplejwt_pair'),
    # returns token + user_data
    url(r'^social/jwt-pair-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTPairUserAuthView.as_view(),
        name='login_social_simplejwt_pair_user'),
)
