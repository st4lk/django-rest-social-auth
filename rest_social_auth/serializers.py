import warnings

from django.utils.module_loading import import_string
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
        # Custom user model may not have some fields from the list below,
        # excluding them based on actual fields
        exclude = [
            field for field in (
                'is_staff', 'is_active', 'date_joined', 'password', 'last_login',
                'user_permissions', 'groups', 'is_superuser',
            ) if field in [mfield.name for mfield in get_user_model()._meta.get_fields()]
        ]


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
            warnings.warn(
                'django-rest-knox must be installed for Knox authentication',
                ImportWarning,
            )
            raise

        token_instance, token_key = AuthToken.objects.create(obj)
        return token_key


class UserKnoxSerializer(KnoxSerializer, UserSerializer):
    pass


class JWTBaseSerializer(serializers.Serializer):

    jwt_token_class_name = None

    def get_token_instance(self):
        if not hasattr(self, '_jwt_token_instance'):
            if self.jwt_token_class_name is None:
                raise NotImplementedError('Must specify `jwt_token_class_name` property')
            if '.' not in self.jwt_token_class_name:
                # Maintain compatibility with class name without module path
                module_path = 'rest_framework_simplejwt.tokens'
                self.jwt_token_class_name = f'{module_path}.{self.jwt_token_class_name}'
            try:
                token_class = import_string(self.jwt_token_class_name)
            except ImportError:
                warnings.warn(
                    'djangorestframework_simplejwt must be installed for JWT authentication',
                    ImportWarning,
                )
                raise
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

    jwt_token_class_name = 'rest_framework_simplejwt.tokens.RefreshToken'

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

    jwt_token_class_name = 'rest_framework_simplejwt.tokens.SlidingToken'

    def get_token(self, obj):
        return str(self.get_token_instance())


class UserJWTSlidingSerializer(JWTSlidingSerializer, UserSerializer):

    def get_token_payload(self, user):
        payload = dict(UserSerializer(user).data)
        payload.pop('id', None)
        return payload
