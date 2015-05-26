from django.conf.urls import include, url
from django.contrib import admin

from users.views import HomeView, LogoutSessionView, UserDetailView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^api/login/', include('rest_social_auth.urls_session')),
    url(r'^api/login/', include('rest_social_auth.urls_token')),

    url(r'^api/logout/session/$', LogoutSessionView.as_view(), name='logout_session'),
    url(r'^api/user/', UserDetailView.as_view(), name="current_user"),
    url(r'^admin/', include(admin.site.urls)),
]
