from django.urls import re_path

from . import views


urlpatterns = (
    # returns knox token + user_data
    re_path(r'^social/knox_user/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialKnoxUserAuthView.as_view(),
            name='login_social_knox_user'),

    # returns knox token only
    re_path(r'^social/knox/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$',
            views.SocialKnoxOnlyAuthView.as_view(),
            name='login_social_knox'),
)
