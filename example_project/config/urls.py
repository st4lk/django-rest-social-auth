from django.contrib import admin
from django.urls import include, re_path

from users import views

urlpatterns = [
    re_path(r'^$', views.HomeSessionView.as_view(), name='home'),
    re_path(r'^session/$', views.HomeSessionView.as_view(), name='home_session'),
    re_path(r'^token/$', views.HomeTokenView.as_view(), name='home_token'),
    re_path(r'^jwt/$', views.HomeJWTView.as_view(), name='home_jwt'),
    re_path(r'^knox/$', views.HomeKnoxView.as_view(), name='home_knox'),

    re_path(r'^api/login/', include('rest_social_auth.urls_session')),
    re_path(r'^api/login/', include('rest_social_auth.urls_token')),
    re_path(r'^api/login/', include('rest_social_auth.urls_jwt_pair')),
    re_path(r'^api/login/', include('rest_social_auth.urls_jwt_sliding')),
    re_path(r'^api/login/', include('rest_social_auth.urls_knox')),

    re_path(r'^api/logout/session/$', views.LogoutSessionView.as_view(), name='logout_session'),
    re_path(r'^api/user/session/',
            views.UserSessionDetailView.as_view(),
            name="current_user_session"),
    re_path(r'^api/user/token/', views.UserTokenDetailView.as_view(), name="current_user_token"),
    re_path(r'^api/user/jwt/', views.UserJWTDetailView.as_view(), name="current_user_jwt"),
    re_path(r'^api/user/knox/', views.UserKnoxDetailView.as_view(), name="current_user_knox"),

    re_path(r'^admin/', admin.site.urls),
]
