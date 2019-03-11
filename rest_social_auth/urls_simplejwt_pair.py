from django.conf.urls import url

from . import views


urlpatterns = (
    url(r'^social/jwt-pair/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSimpleJWTPairOnlyAuthView.as_view(),
        name='login_social_simplejwt_pair'),)
