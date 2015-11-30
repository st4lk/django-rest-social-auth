from django.views.generic import TemplateView
from django.contrib.auth import logout, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_social_auth.serializers import UserSerializer
from rest_framework.authentication import SessionAuthentication, TokenAuthentication


class HomeView(TemplateView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        if self.kwargs.get('auth_type') == 'token':
            return ['home_token.html']
        else:
            return ['home_session.html']

class LogoutSessionView(APIView):

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseDeatilView(generics.RetrieveAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = UserSerializer
    model = get_user_model()

    def get_object(self, queryset=None):
        return self.request.user


class UserSessionDetailView(BaseDeatilView):
    authentication_classes = (SessionAuthentication, )


class UserTokenDetailView(BaseDeatilView):
    authentication_classes = (TokenAuthentication, )
