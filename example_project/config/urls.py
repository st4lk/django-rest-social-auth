from django.conf.urls import include, url
from django.contrib import admin

from users import views

urlpatterns = [
    url(r'^$', views.HomeSessionView.as_view(), name='home'),
    url(r'^session/$', views.HomeSessionView.as_view(), name='home_session'),
    url(r'^token/$', views.HomeTokenView.as_view(), name='home_token'),
    url(r'^jwt/$', views.HomeJWTView.as_view(), name='home_jwt'),

    url(r'^api/login/', include('rest_social_auth.urls_session')),
    url(r'^api/login/', include('rest_social_auth.urls_token')),
    url(r'^api/login/', include('rest_social_auth.urls_jwt')),

    url(r'^api/logout/session/$', views.LogoutSessionView.as_view(), name='logout_session'),
    url(r'^api/user/session/', views.UserSessionDetailView.as_view(), name="current_user_session"),
    url(r'^api/user/token/', views.UserTokenDetailView.as_view(), name="current_user_token"),
    url(r'^api/user/jwt/', views.UserJWTDetailView.as_view(), name="current_user_jwt"),
    url(r'^admin/', include(admin.site.urls)),
]
