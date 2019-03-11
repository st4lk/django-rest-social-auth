from django.conf.urls import url

from . import views


urlpatterns = (
    url(r'^social/jwt-sliding/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTSlidingOnlyAuthView.as_view(),
        name='login_social_simplejwt_sliding'),)
