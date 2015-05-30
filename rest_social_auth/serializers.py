# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


class SocialAuthInputSerializer(serializers.Serializer):
    provider = serializers.CharField()
    code = serializers.CharField()
    redirect_uri = serializers.URLField(required=False)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_active', 'date_joined', 'password',
            'last_login', 'user_permissions', 'groups', 'is_superuser')


class TokenSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class UserTokenSerializer(TokenSerializer, UserSerializer):
    pass
