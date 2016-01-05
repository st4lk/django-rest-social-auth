from django.conf.urls import url

from . import views


urlpatterns = (
    # returns token + user_data
    url(r'^social/token_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialTokenUserAuthView.as_view(),
        name='login_social_token_user'),

    # returns token only
    url(r'^social/token/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialTokenOnlyAuthView.as_view(),
        name='login_social_token'),)
