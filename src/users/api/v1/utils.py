import jwt
import requests
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


def get_id_token(token):
    client_id, client_secret = get_key_and_secret()
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": token,
        "grant_type": "authorization_code",
        "redirect_uri": "https://giftsolitare.com/xxxxx",
    }

    res = requests.post(
        "https://appleid.apple.com/auth/token", data=payload, headers=headers
    )
    response_dict = res.json()
    id_token = response_dict.get("id_token", None)
    return id_token


def get_key_and_secret():
    headers = {"kid": settings.APPLE_ID_KEY}

    payload = {
        "iss": settings.APPLE_ID_TEAM,
        "iat": timezone.now(),
        "exp": timezone.now() + timedelta(days=180),
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_ID_CLIENT,
    }

    client_secret = jwt.encode(
        payload,
        settings.APPLE_ID_SECRET,
        algorithm="ES256",
        headers=headers,
    )

    return settings.APPLE_ID_CLIENT, client_secret
