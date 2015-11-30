from django.conf.urls import include, url
from django.contrib import admin

from users import views

urlpatterns = [
    url(r'^(?P<auth_type>(?:session|token)?)/?$', views.HomeView.as_view(), name='home'),

    url(r'^api/login/', include('rest_social_auth.urls_session')),
    url(r'^api/login/', include('rest_social_auth.urls_token')),

    url(r'^api/logout/session/$', views.LogoutSessionView.as_view(), name='logout_session'),
    url(r'^api/user/session/', views.UserSessionDetailView.as_view(), name="current_user_session"),
    url(r'^api/user/token/', views.UserTokenDetailView.as_view(), name="current_user_token"),
    url(r'^admin/', include(admin.site.urls)),
]
