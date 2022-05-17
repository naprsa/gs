from djoser.conf import settings


TOKEN_SERIALIZER_ERROR_MESSAGES = {
    "invalid_token": "Auth token invalid or missing",
    "token_expired": "provider token expired",
    "invalid_id_token": "Invalid or missing id_token from apple",
    "verification_fail": "Token verification failed",
    "inactive_account": settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
}
