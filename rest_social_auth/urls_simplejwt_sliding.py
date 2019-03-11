from django.conf.urls import url

from . import views


urlpatterns = (
    # returns token only
    url(r'^social/jwt-sliding/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTSlidingOnlyAuthView.as_view(),
        name='login_social_simplejwt_sliding'),
    # returns token + user_data
    url(r'^social/jwt-sliding-user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTSlidingUserAuthView.as_view(),
        name='login_social_simplejwt_sliding_user'),
)
