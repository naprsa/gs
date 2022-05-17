from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from djoser.conf import settings
from djoser import utils
from .serializers import (
    AppleLoginSerializer,
    GoogleLoginSerializer,
    UserProfileSerializer,
)
from ...models import User


class TokenLogin(utils.ActionViewMixin, generics.GenericAPIView):
    """
    ### Errors:
        INVALID_TOKEN: Auth token invalid or missing,
        AUTH_TOKEN_ERROR: Invalid or missing id_token from apple,
        VERIFICATION_FAIL: Token verification failed",
        INACTIVE_ACCOUNT: User account is disabled,
        INVALID_CREDENTIALS_ERROR: Unable to log in with provided credentials.
        INACTIVE_ACCOUNT_ERROR: User account is disabled.
        INVALID_TOKEN_ERROR: Invalid token for given user.
    """

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def post(self, request, **kwargs):
        if request.data.get("provider"):
            if request.data.get("provider") == "apple":
                self.serializer_class = AppleLoginSerializer
            if request.data.get("provider") == "google":
                self.serializer_class = GoogleLoginSerializer

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )


class UserApiView(generics.RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = self.filter_queryset(self.get_object())
        self.check_object_permissions(self.request, queryset)
        return queryset

    def get_object(self):
        return self.request.user
