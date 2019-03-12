from importlib import import_module
import warnings

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class OAuth2InputSerializer(serializers.Serializer):

    provider = serializers.CharField(required=False)
    code = serializers.CharField()
    redirect_uri = serializers.CharField(required=False)


class OAuth1InputSerializer(serializers.Serializer):

    provider = serializers.CharField(required=False)
    oauth_token = serializers.CharField()
    oauth_verifier = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        exclude = (
            'is_staff', 'is_active', 'date_joined', 'password', 'last_login', 'user_permissions',
            'groups', 'is_superuser',
        )


class TokenSerializer(serializers.Serializer):

    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class UserTokenSerializer(TokenSerializer, UserSerializer):
    pass


class KnoxSerializer(TokenSerializer):
    def get_token(self, obj):
        try:
            from knox.models import AuthToken
        except ImportError:
            warnings.warn('django-rest-knox must be installed for Knox authentication', ImportWarning)
            raise

        token = AuthToken.objects.create(obj)
        return token


class UserKnoxSerializer(KnoxSerializer, UserSerializer):
    pass


class JWTBaseSerializer(serializers.Serializer):

    jwt_token_class_name = None

    def get_token_instance(self):
        if not hasattr(self, '_jwt_token_instance'):
            if self.jwt_token_class_name is None:
                raise NotImplementedError('Must specify `jwt_token_class_name` property')
            try:
                tokens_module = import_module('rest_framework_simplejwt.tokens')
            except ImportError:
                warnings.warn(
                    'djangorestframework_simplejwt must be installed for JWT authentication',
                    ImportWarning,
                )
                raise
            token_class = getattr(tokens_module, self.jwt_token_class_name)
            user = self.instance
            self._jwt_token_instance = token_class.for_user(user)
            for key, value in self.get_token_payload(user).items():
                self._jwt_token_instance[key] = value
        return self._jwt_token_instance

    def get_token_payload(self, user):
        """
        Payload defined here will be added to default mandatory payload.
        Receive User instance in argument, returns dict.
        """
        return {}


class JWTPairSerializer(JWTBaseSerializer):
    token = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()

    jwt_token_class_name = 'RefreshToken'

    def get_token(self, obj):
        return str(self.get_token_instance().access_token)

    def get_refresh(self, obj):
        return str(self.get_token_instance())


class UserJWTPairSerializer(JWTPairSerializer, UserSerializer):

    def get_token_payload(self, user):
        payload = dict(UserSerializer(user).data)
        payload.pop('id', None)
        return payload


class JWTSlidingSerializer(JWTBaseSerializer):
    token = serializers.SerializerMethodField()

    jwt_token_class_name = 'SlidingToken'

    def get_token(self, obj):
        return str(self.get_token_instance())


class UserJWTSlidingSerializer(JWTSlidingSerializer, UserSerializer):

    def get_token_payload(self, user):
        payload = dict(UserSerializer(user).data)
        payload.pop('id', None)
        return payload


# Depcreated Seraizlisers
class JWTSerializer(TokenSerializer):

    def get_token(self, obj):
        warnings.warn(
            'Support of djangorestframework-jwt will be removed in 3.0.0 version. '
            'Use rest_framework_simplejwt instead.',
            DeprecationWarning,
        )
        try:
            from rest_framework_jwt.settings import api_settings
        except ImportError:
            warnings.warn('djangorestframework-jwt must be installed for JWT authentication',
                          ImportWarning)
            raise

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self.get_jwt_payload(obj))
        token = jwt_encode_handler(payload)

        return token

    def get_jwt_payload(self, obj):
        """
        Define here, what data shall be encoded in JWT.
        By default, entire object will be encoded.
        """
        return obj


class UserJWTSerializer(JWTSerializer, UserSerializer):
    pass
