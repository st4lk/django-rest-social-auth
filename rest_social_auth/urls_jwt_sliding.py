from django.conf.urls import url

from . import views


urlpatterns = (
    # returns token only
    url(r'^social/jwt-sliding/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTSlidingOnlyAuthView.as_view(),
        name='login_social_jwt_sliding'),
    # returns token + user_data
    url(r'^social/jwt-sliding-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialJWTSlidingUserAuthView.as_view(),
        name='login_social_jwt_sliding_user'),
)
