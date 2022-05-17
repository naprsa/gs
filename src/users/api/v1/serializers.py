from icecream import ic
from rest_framework import serializers
from django.conf import settings
import jwt
from jwt import PyJWTError
from google.oauth2 import id_token
from google.auth.transport import requests
from .messages import TOKEN_SERIALIZER_ERROR_MESSAGES
from users.models import AuthProvider, User
from .utils import get_id_token


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    default_error_messages = TOKEN_SERIALIZER_ERROR_MESSAGES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        token = attrs.get("token")
        if not token:
            self.fail("invalid_token")
        try:
            response = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError as e:
            ic(e)
            self.fail("token_expired")

        params = {}
        params.update({"email": response["email"]}) if "email" in response else None
        params.update({"uid": response["sub"]}) if "sub" in response else None

        self.user = self.authenticate(**params)

        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")

    def authenticate(self, email=None, uid=None):
        if not email or not uid:
            self.fail("invalid_credentials")

        provider, created = AuthProvider.objects.get_or_create(uid=uid, name="google")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email)

        user.provider = provider
        user.save(update_fields=["provider"])
        return user


class AppleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    default_error_messages = TOKEN_SERIALIZER_ERROR_MESSAGES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        token = attrs.get("token")
        params = {}

        if not token:
            self.fail("invalid_token")

        # if not settings.DEBUG:
        id_token = get_id_token(token)
        if not id_token:
            self.fail("invalid_id_token")

        try:
            decoded = jwt.decode(id_token, "", verify=False)
        except PyJWTError as e:
            self.fail("verification_fail")

        params.update({"email": decoded["email"]}) if "email" in decoded else None
        params.update({"uid": decoded["sub"]}) if "sub" in decoded else None
        # else:
        #     params.update({"email": "test@test.ru"})
        #     params.update({"uid": "000000000000"})

        self.user = self.authenticate(**params)

        if self.user and self.user.is_active:
            return attrs

        self.fail("invalid_credentials")

    def authenticate(self, email=None, uid=None):
        if not email or not uid:
            self.fail("invalid_credentials")

        provider, created = AuthProvider.objects.get_or_create(uid=uid, name="apple")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email)

        user.provider = provider
        user.save(update_fields=["provider"])
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    provider = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = User
        fields = ["uid", "email", "provider"]
