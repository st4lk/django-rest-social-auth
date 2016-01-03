from django.conf.urls import url

from . import views


urlpatterns = (
    url(r'^social/session/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
        views.SocialSessionAuthView.as_view(),
        name='login_social_session'),)
